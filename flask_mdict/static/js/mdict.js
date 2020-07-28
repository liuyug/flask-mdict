
function mdict_click(element, event) {
    let url = element.href;
    console.log(element, event);
    event.preventDefault();
    if (url.lastIndexOf('sound://', 0) === 0){
        if (element.hasAttribute('abs_url')) {
            url = url.replace("sound://", "http://");
        } else {
            url = url.replace("sound://", "");
        }
        let mdict_player = document.createElement("audio");
        mdict_player.id = 'mdict_player';
        mdict_player.src = url;
        console.log('play', url);
        mdict_player.play();
    } else if (url.lastIndexOf('entry://', 0) === 0){
        if (element.hasAttribute('abs_url')) {
            url = url.replace("entry://", "http://");
        } else {
            url = url.replace("entry://", "");
        }
        window.location = url;
    }
}
