
function click_sound(url) {
    return function (event) {
        // prevent default action: jump by a.href
        event.preventDefault();
        // prevent other event listener
        event.stopPropagation();
        let mdict_player = document.createElement("audio");
        mdict_player.id = 'mdict_player';
        mdict_player.src = url;
        mdict_player.play();
    }
}

function click_entry(url) {
    return function (event) {
        // prevent default action: jump by a.href
        event.preventDefault();
        // prevent other event listener
        event.stopPropagation();
        window.location.href = url;
    }
}

for (let element of document.getElementsByTagName('A')) {
    if (element.href) {
        let url = element.href;
        if (element.href.startsWith('sound://')) {
            if (element.hasAttribute('abs_url')) {
                url = url.replace("sound://", "http://");
            } else {
                url = url.replace("sound://", "");
            }
            element.addEventListener('click', click_sound(url));
        }
        if (element.href.startsWith('entry://')) {
            if (element.hasAttribute('abs_url')) {
                url = url.replace("entry://", "http://");
            } else {
                url = url.replace("entry://", "");
            }
            element.addEventListener('click', click_entry(url));
        }
    }
}
