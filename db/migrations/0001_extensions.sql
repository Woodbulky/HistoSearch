-- 0001: extensions and shared enums
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Conflict classification (CLAUDE.md Contribution A). UNKNOWN must remain available.
DO $$ BEGIN
    CREATE TYPE conflict_label AS ENUM (
        'NOT_CONTRADICTION',
        'RESOLVABLE_BY_RECENCY',
        'PERMANENTLY_CONTESTED',
        'UNKNOWN'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Temporal granularity: never record an event time more precisely than the source supports.
DO $$ BEGIN
    CREATE TYPE time_granularity AS ENUM ('day', 'month', 'year', 'decade', 'unknown');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE entity_type AS ENUM ('PERSON', 'PLACE', 'ORGANIZATION', 'OTHER');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE node_kind AS ENUM ('entity', 'event', 'claim', 'document', 'passage');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
