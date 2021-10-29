# 03 — Buttons

The goal of this challenge is to implement some reusable buttons for you games.

Simulating is button is somewhat simple, but can also start to be quite complex, especially
if you want it well design, so the hallenge should be accessible to everyone.
It will also be quite useful later to have some button class that you can just pop in your code
and reuse every time you need buttons in a game / project.

### Achievements

 Description of the different levels and the amount of 
`C`hallenger `P`oints they provide:

- Casual `+3 CP`: Make reusable buttons that you can easily add into any project.
    Buttons need to support a background color, some text content and a nice way to
    define the action that happens when a user clicks them. 
    Also, make them look as good as you can!
- Ambitious `+2 CP`: Make full-featured buttons, with hovering, double click, optional icon,
    give feedback when the button is clicked (visual, but maybe sound too ?).
    This is also a design challenge, that is, the buttons must look *and* feel good from a user point
    of view.
- Adventurous `+1 CP`: Implement ninepatch textures for your buttons (search about this cool technique on internet!)
    

In any case, remember to always try to make things as reusable as possible,
who know, you may need it in a future project!
If you are wondering what your buttons can do, you can make them spawn particles if you
did the previous challenge. If you did not, you can make them draw stuff on the screen,
and for instance have a button that draws a circle, one that draws a rectangle at a random place...
Even simpler could just be to change the color of the background or of some button.

Bonus: You win 420 virtual fame points if you make a simple game using *only* your buttons!

### What is Ninepatch?

(Summarized from https://ichi.pro/de/erstellen-sie-in-der-grosse-veranderbare-bitmaps-9-patch-dateien-80021496218918)

Ninepatch is a system that divides an image into 9 different sections where each section reacts in a different way when being scaled:

![1_zuenDjgdkTEmtLClvRe4fg](https://user-images.githubusercontent.com/85095943/139265360-eb228192-9527-4b12-bfd4-df0fcc1b1403.png)

**Corner Regions (1, 3, 7, 9)** These regions are fixed and nothing in them will stretch.

**Horizontal sides (4, 6)** The pixels in this area are stretched or repeated vertically if necessary.

**Vertical sides (2, 8)** The pixels in this area are stretched or repeated horizontally if necessary. 

**Center (5)** The pixels in this area are stretched evenly in both the horizontal and vertical directions.

This is useful because it allows for button images to be streched based on the text that hold without loosing the roundness on the corners of the image

Let take a look at an example:

The image below is of a text box with a resolution of 258x141

![ninepatch_bubble 9](https://user-images.githubusercontent.com/85095943/139268352-a13d9587-f198-432c-aabd-50890177da60.png)

Lets say we want to resize this text box to a resolution of 200x200. the top image represents what the text box would look like if we did this using a ninepatch texture and the bottom image would demonstrate what would happen if you simpily resized the image to 200x200 (in this case using `pygame.transform.scale(image, (200,200))`) 

![Capture](https://user-images.githubusercontent.com/85095943/139269034-97bada52-7c3f-47df-ae41-643eba41687e.PNG)

As you can clearly see, the top image has maintained the correct resolution on the corners whilst the bottom image has not.

### Setup

The setup code in [`base/`](./base) consists of mostly of a simple pygame template. 
There is also a suggested interface for your buttons to help you get started
and some utilities to draw text and load images, but that's it.

To get started, **duplicate** the whole `base` folder and rename the copy with your username
(we will call it `yourname/` from now on). All your modifications should be inside the `yourname/` folder,
otherwise it would be impossible to have a showcase of all the submissions.

> PLEASE. Do not modify the base folder.

Further instructions and tips are [available on this document](../general_instructions.md).

Have fun !

### Credits

 - Setup code: [CozyFractal](https://cozyfractal.com)

### Legal stuff

By submitting your game, you agree that we add its code to the repository 
and that it can be:
- used (for instance in the showcase), 
- modified (for instance to work with a future version of the showcase),
- shared (for instance as a mean to illustrate the capabilities of pygames).

But all those uses must be for the good of the community, and never for any individual.
This concerns for instance any profits that could be made: they have to be used for the 
benefit of the whole community.
