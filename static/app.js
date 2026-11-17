// Mismo app.js del ejercicio LOGIN (PHP): revisa en el navegador que las contraseñas coincidan.

const formRegistro = document.getElementById('form-registro');

formRegistro.addEventListener('submit', (evento) => {
    const password = formRegistro.password.value;
    const confirmar = formRegistro.confirmar.value;

    if (password !== confirmar) {
        evento.preventDefault();
        alert('Las contraseñas no coinciden.');
    }
});
