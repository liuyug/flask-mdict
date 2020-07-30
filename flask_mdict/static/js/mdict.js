
function mdict_click(element, event) {
    let url = element.href;
    // prevent default action: jump by a.href
    event.preventDefault();
    // prevent other event listener
    event.stopPropagation();
    if (url.lastIndexOf('sound://', 0) === 0){
        if (element.hasAttribute('abs_url')) {
            url = url.replace("sound://", "http://");
        } else {
            url = url.replace("sound://", "");
        }
        let mdict_player = document.createElement("audio");
        mdict_player.id = 'mdict_player';
        mdict_player.src = url;
        mdict_player.play();
    } else if (url.lastIndexOf('entry://', 0) === 0){
        if (element.hasAttribute('abs_url')) {
            url = url.replace("entry://", "http://");
        } else {
            url = url.replace("entry://", "");
        }
        window.location.href = url;
    }
}
