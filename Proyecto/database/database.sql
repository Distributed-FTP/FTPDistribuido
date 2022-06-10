CREATE DATABASE "FTPDistributedDB"
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Cuba.1252'
    LC_CTYPE = 'Spanish_Cuba.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

CREATE TABLE public."Directories"
(
    id integer NOT NULL,
    directory character varying(100) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "Directories_pkey" PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public."Directories"
    OWNER to postgres;

CREATE TABLE public."User"
(
    id integer NOT NULL,
    name character varying(25) COLLATE pg_catalog."default" NOT NULL,
    password character varying(25) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "User_pkey" PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public."User"
    OWNER to postgres;

CREATE TABLE public."UsersByDirectories"
(
    id integer NOT NULL,
    user_id integer NOT NULL,
    directory_id integer NOT NULL,
    CONSTRAINT "ID" PRIMARY KEY (id),
    CONSTRAINT directory_id FOREIGN KEY (directory_id)
        REFERENCES public."Directories" (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT user_id FOREIGN KEY (user_id)
        REFERENCES public."User" (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)

TABLESPACE pg_default;

ALTER TABLE public."UsersByDirectories"
    OWNER to postgres;