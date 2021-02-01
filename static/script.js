const NEW_HEIGHT = "120px"
const FOREGROUND_INDEX = 5

let prevHeight = ""

window.onload = () => {

    const enter = (event) => {

        const bgButton = event.target.childNodes[FOREGROUND_INDEX]
        console.log(bgButton);

        prevHeight = bgButton.style.height
        bgButton.style.height = NEW_HEIGHT
    }

    const leave = (event) => {
        const bgButton = event.target.childNodes[FOREGROUND_INDEX]
        console.log(bgButton);
        bgButton.style.height = prevHeight
    }


    // document.querySelectorAll('.button').forEach(item => {

    //     item.addEventListener('mouseenter', enter)
    //     item.addEventListener('mouseleave', leave)
    // })
        
};

