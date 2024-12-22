CREATE TABLE train (
  id INTEGER PRIMARY KEY,
  server TEXT NOT NULL,
  train_number TEXT NOT NULL,
  composition TEXT NOT NULL,
  vd_index INTEGER NOT NULL,
  first_seen INTEGER NOT NULL,
  last_seen INTEGER NOT NULL,
  first_seen_server INTEGER NOT NULL,
  last_seen_server INTEGER NOT NULL
) STRICT;

CREATE INDEX train_ord ON train (server, train_number, last_seen);
