const LOADING = "/static/noun-loading-5531341.png"
const ERROR = "/static/noun-error-1073622.png"

// just putting it in an asyc function for await...
async function load (){
    // just do this for all divs.
    like_buttons = document.getElementsByClassName("pen_like_1")
    for (let i = 0; i < like_buttons.length; i++) {
        // get the div and pull the Id from the data-attribute
        let like_div = like_buttons[i]; 
        let id = like_div.getAttribute("data-id")
        
        // create an image for status update.
        let image = document.createElement("img")
        image.src = LOADING
        like_div.append(image)

        // because I'm lazy, I throw the entier thing in a try catch...
        try {    
            // get the like count.
            let result = await fetch('/pen/'+id+'/like')
            if(!result.ok) throw new Error("not ok");
            result = await result.json()
            let likes = result.likes
            let you_like = result.you_like

            // function for updating display.
            function update() {
                like_div.textContent = likes
                if(you_like) {
                    like_div.style['background-color'] = 'green';
                } else {
                    like_div.style['background-color'] = '';
                }
                
            }
            update();

            // on click
            like_div.addEventListener("click", async () => {

                // like or unlike
                try {
                    let method = "POST"
                    if (you_like) {
                        method = "DELETE"
                    }
                    // set the spinner
                    like_div.textContent=""
                    like_div.append(image);
                    // send the reqest
                    let result = await fetch('/pen/'+id+'/like1', {method})
                    if(!result.ok) throw new Error("not ok");
                    // process results
                    result = await result.json()
                    likes = result.likes
                    you_like = result.you_like
                    update()
                } catch (error) {
                    console.log(error)
                    like_div.textContent="";
                    image.src = ERROR
                    like_div.append(image);
                }
            })
        } catch (error) {
            console.log(error)
            like_div.textContent="";
            image.src = ERROR
            like_div.append(image);
        }
    }
}
load();