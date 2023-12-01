/*!
    * Start Bootstrap - SB Admin v7.0.7 (https://startbootstrap.com/template/sb-admin)
    * Copyright 2013-2023 Start Bootstrap
    * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-sb-admin/blob/master/LICENSE)
    */
    // 
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

});

const file = document.getElementById('foto');
const img = document.getElementById('img');
const perfilImg = document.getElementById('perfil-img');

file.addEventListener('change', e => {
    if (e.target.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            img.src = e.target.result;
            perfilImg.src = e.target.result;
            
            // Guardar la imagen en el almacenamiento local del navegador
            localStorage.setItem('perfilImage', e.target.result);
        }
        reader.readAsDataURL(e.target.files[0]);
    } else {
        img.src = defaultFile;
        perfilImg.src = defaultFile;

        // Restablecer el almacenamiento local del navegador al valor predeterminado
        localStorage.removeItem('perfilImage');
    }
});

// Comprobar si hay una imagen almacenada en el almacenamiento local del navegador
const storedImage = localStorage.getItem('perfilImage');
if (storedImage) {
    img.src = storedImage;
    perfilImg.src = storedImage;
}
