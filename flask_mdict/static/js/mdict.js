
function click_sound(event) {
    // prevent default action: jump by a.href
    event.preventDefault();
    // prevent other event listener
    event.stopPropagation();
    let url = this.getAttribute('data-sound-url');
    let mdict_player = document.createElement("audio");
    mdict_player.id = 'mdict_player';
    mdict_player.src = url;
    mdict_player.play();
}

function click_entry(event) {
    // prevent default action: jump by a.href
    event.preventDefault();
    // prevent other event listener
    event.stopPropagation();
    let url = this.getAttribute('data-entry-url');
    window.location.href = url;
}

for (let element of document.getElementsByTagName('A')) {
    if (element.href) {
        let url = element.href;
        if (element.href.startsWith('sound://')) {
            element.addEventListener('click', click_sound);
        } else if (element.href.startsWith('entry://')) {
            element.addEventListener('click', click_entry);
        }
    }
}
