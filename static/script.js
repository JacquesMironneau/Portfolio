
window.onload = () => {
    console.log("Script loaded");

    // let buttons = document.getElementsByClassName("button");

    // const buttons = document.getElementsByClassName("button");

    const enter = () => {

        console.log("you entered");
    }

    const leave = () => {
        console.log("you leaved");

    }
    document.querySelectorAll('.button').forEach(item => {

        item.addEventListener('mouseenter', enter)
        item.addEventListener('mouseleave',leave)
    })
        
};

