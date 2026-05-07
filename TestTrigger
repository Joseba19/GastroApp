DELIMITER //

CREATE TRIGGER trg_empleado_login
AFTER INSERT ON empleados
FOR EACH ROW
BEGIN
    IF NEW.puesto = 'docente' OR NEW.puesto = 'cocinero' THEN
        INSERT INTO usuarios_login (NEW.id_empleado, NEW.usuario, password_hash, activo)
        VALUES(
NEW.id_empleado,
username fn_generar_username(p_id_empleado NEW.id_empleado),
password_hash
activo 1
);
    END IF;
END //

DELIMITER ;
