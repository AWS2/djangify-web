<?php
    // Cargar autoload desde vendor en scripts/
    require __DIR__ . '/vendor/autoload.php';

    use Dotenv\Dotenv;

    // Solo subimos 3 niveles hasta djangify-web/
    $dotenv = Dotenv::createImmutable(__DIR__ . '/../../..');
    $dotenv->load();

    use PHPMailer\PHPMailer\PHPMailer;
    use PHPMailer\PHPMailer\Exception;

    // Configuración base de datos (variables desde .env)
    $host = $_ENV['DATABASE_HOST'];
    $db = $_ENV['DATABASE_NAME'];
    $user = $_ENV['DATABASE_USER'];
    $password = $_ENV['DATABASE_PASSWORD'];

    // Conexión a MySQL
    $mysqli = new mysqli($host, $user, $password, $db);
    if ($mysqli->connect_error) {
        die("Error de conexión: " . $mysqli->connect_error);
    }

    // Obtener hasta 20 correos no enviados
    $query = "SELECT m.id, m.subject, m.body, u.email 
            FROM myweb_mail m
            INNER JOIN myweb_usuario u ON m.user_id = u.id
            WHERE m.send = 0
            LIMIT 20";

    $result = $mysqli->query($query);

    // Configuración PHPMailer con Gmail SMTP
    $mail = new PHPMailer(true);
    $mail->isSMTP();
    $mail->Host = 'smtp.gmail.com';
    $mail->SMTPAuth = true;
    $mail->Username = $_ENV['MAIL_USERNAME'];         // Gmail
    $mail->Password = $_ENV['MAIL_PASSWORD'];         // Contraseña de aplicación
    $mail->SMTPSecure = 'tls';
    $mail->Port = 587;
    $mail->setFrom("no-reply@djangify.ieti.site", 'Djangify');
    $mail->addReplyTo('no-reply@djangify.ieti.site', 'No responder');
    $mail->Sender = 'no-reply@djangify.ieti.site';

    if ($result && $result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
            try {
                $mail->clearAddresses();
                $mail->addAddress($row['email']);
                $mail->Subject = $row['subject'];
                $mail->Body    = $row['body'];
                $mail->AltBody = strip_tags($row['body']);

                $mail->send();
                echo "Correo enviado a: {$row['email']}\n";

                $id = intval($row['id']);
                $mysqli->query("UPDATE myweb_mail SET send = 1 WHERE id = $id");
            } catch (Exception $e) {
                echo "Error al enviar a {$row['email']}: {$mail->ErrorInfo}\n";
            }
        }
    } else {
        echo "No hay correos pendientes\n";
    }

    $mysqli->close();
?>