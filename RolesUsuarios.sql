CREATE ROLE 'rol_lectura';
CREATE ROLE 'rol_admin';

GRANT SELECT ON gastrolab.* TO 'rol_lectura';
GRANT ALL PRIVILEGES ON gastrolab.* TO 'rol_admin';

FLUSH PRIVILEGES;

CREATE USER 'lector1'@'%' IDENTIFIED BY '1234';
CREATE USER 'lector2'@'%' IDENTIFIED BY '1234';
CREATE USER 'admin'@'%' IDENTIFIED BY '1234';

GRANT 'rol_lectura' TO 'lector1'@'%';
GRANT 'rol_lectura' TO 'lector2'@'%';
GRANT 'rol_admin' TO 'admin'@'%';

FLUSH PRIVILEGES;
