CREATE ROLE 'rol_lectura';
CREATE ROLE 'rol_admin';

GRANT SELECT ON gastrolab.* TO 'rol_lectura';
GRANT ALL PRIVILEGES ON gastrolab.* TO 'rol_admin';

FLUSH PRIVILEGES;

CREATE USER 'lector1'@'%' IDENTIFIED BY '1234';
CREATE USER 'lector2'@'%' IDENTIFIED BY '1234';
CREATE USER 'admin'@'%' IDENTIFIED BY '1234';

GRANT SELECT ON gastrolab.* TO 'lector1'@'%';
GRANT SELECT ON gastrolab.* TO 'lector2'@'%';
GRANT ALL PRIVILEGES ON gastrolab.* TO 'admin'@'%';

FLUSH PRIVILEGES;