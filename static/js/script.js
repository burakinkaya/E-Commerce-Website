const currentLocation = location.href;
const menuItem = document.querySelector('a');
const menuLength = menuItem.length;
for( i = 0; i < menuLength; i++){
    if (menuItem[i].href === currentLocation){
        menuItem[i].className = 'active'
    }
}