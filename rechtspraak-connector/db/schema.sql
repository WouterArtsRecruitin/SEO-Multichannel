-- Rechtspraak API Connector — Supabase / PostgreSQL schema
-- Run in the Supabase SQL editor (or: psql "$DATABASE_URL" -f db/schema.sql)
--
-- Design note (AI-readiness, requirement 6):
--   metadata (structured) is kept SEPARATE from the body text (`inhoud`),
--   so a future RAG/MCP agent can chunk + embed `inhoud` while filtering on
--   the columns/jsonb metadata. A ready-to-use chunk table is included below
--   (optional, needs the pgvector extension).

create table if not exists public.uitspraken (
    ecli            text primary key,                 -- ECLI:NL:HR:2012:1312
    type            text,                              -- 'uitspraak' | 'conclusie'
    titel           text,
    samenvatting    text,
    instantie       text,                              -- dcterms:creator
    rechtsgebieden  text[]        not null default '{}',
    uitspraakdatum  date,                              -- dcterms:date
    publicatiedatum date,                              -- dcterms:issued
    modified        timestamptz,                       -- dcterms:modified
    taal            text,
    zaaknummer      text,
    vindplaatsen    jsonb         not null default '[]'::jsonb,
    deeplink        text,                              -- uitspraken.rechtspraak.nl/...
    source_url      text,                              -- data.rechtspraak.nl/uitspraken/content?id=...
    inhoud          text,                              -- SCHONE hoofdtekst (los van metadata)
    metadata        jsonb         not null default '{}'::jsonb,  -- volledige ruwe metadata
    content_hash    text,                              -- md5(inhoud) → wijziging detecteren
    status          text          not null default 'active',    -- 'active' | 'withdrawn'
    first_seen      timestamptz   not null default now(),
    last_checked    timestamptz   not null default now(),
    updated_at      timestamptz   not null default now()
);

create index if not exists uitspraken_rechtsgebieden_idx on public.uitspraken using gin (rechtsgebieden);
create index if not exists uitspraken_uitspraakdatum_idx on public.uitspraken (uitspraakdatum desc);
create index if not exists uitspraken_status_idx        on public.uitspraken (status);
create index if not exists uitspraken_instantie_idx     on public.uitspraken (instantie);

-- Run-logboek: elke nachtelijke run laat hier een regel na (observability).
create table if not exists public.run_log (
    id            bigint generated always as identity primary key,
    started_at    timestamptz not null default now(),
    finished_at   timestamptz,
    modified_from timestamptz,                          -- incrementele grens van deze run
    found         integer not null default 0,
    inserted      integer not null default 0,
    updated       integer not null default 0,
    withdrawn     integer not null default 0,
    errors        integer not null default 0,
    ok            boolean not null default false,
    notes         jsonb   not null default '{}'::jsonb
);

-- Automatische updated_at
create or replace function public.set_updated_at() returns trigger as $$
begin new.updated_at := now(); return new; end; $$ language plpgsql;

drop trigger if exists trg_uitspraken_updated_at on public.uitspraken;
create trigger trg_uitspraken_updated_at
    before update on public.uitspraken
    for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- OPTIONEEL — voorbereiding op RAG/MCP-chat (activeer wanneer je zover bent):
--
--   create extension if not exists vector;
--
--   create table if not exists public.uitspraak_chunks (
--       id          bigint generated always as identity primary key,
--       ecli        text not null references public.uitspraken(ecli) on delete cascade,
--       chunk_index integer not null,
--       inhoud      text not null,
--       embedding   vector(1536),           -- pas dim aan je embedding-model aan
--       created_at  timestamptz not null default now(),
--       unique (ecli, chunk_index)
--   );
--   create index on public.uitspraak_chunks using ivfflat (embedding vector_cosine_ops);
-- ---------------------------------------------------------------------------
