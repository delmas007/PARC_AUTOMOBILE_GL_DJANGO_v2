const button = document.getElementById('avatar-navbars');
const closeButton = document.querySelector('.close-button');
const navigationMenu = document.querySelector('.navigation__menu');
let menuIsOpen = false;

button.addEventListener('click', () => {
    navigationMenu.classList.remove('none');
    navigationMenu.classList.remove('hide');
    menuIsOpen = true;
});

closeButton.addEventListener('click', () => {
    navigationMenu.classList.add('hide');
    menuIsOpen = false;
});

document.addEventListener('click', function(event) {
    const isClickInsideMenu = navigationMenu.contains(event.target);
    const isClickInsideButton = button.contains(event.target);

    if (!isClickInsideMenu && !isClickInsideButton && menuIsOpen) {
        navigationMenu.classList.add('hide');
        menuIsOpen = false;
    }
});
