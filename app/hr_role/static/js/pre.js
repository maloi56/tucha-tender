var loader = document.querySelector(".mask")

window.addEventListener("load", vanish);

function vanish() {
  loader.classList.add("disppear");
}

const myButton = document.getElementById("btn");
myButton.addEventListener("click", function() {
  loader.classList.add("show");
});