# PowerPoint template instruction
By default, SkyDock AI Suite uses [powerpoint_template.pptx](resources/powerpoint_template.pptx) as the template for PowerPoint presentation. 

If you want to use your own organization's PowerPoint presentation template, follow these steps **before building the Docker image**:
- Copy a blank (no slide) presentation using your own template to the folder **resources**
- In the configuration file, update the variable TEMPLATE_FILE with the file you just copied
- Update the variable TITLE_TEMPLATE_SLIDE_INDEX with the index of the Title slide. For most PowerPoint template, usually the index of Title slide is 0
- Update the variable CONTENT_TEMPLATE_SLIDE_INDEX with the index of the normal Content slide. This value is different between templates so you need to know which one is the correct index number.

One way to figure that out is to open the PowerPoint file, click on the "New Slide" menu icon and look at the order of different slide templates:
<img src="/images/powerpoint_template_title_slide.png" alt="PowerPoint template Title slide"></img>
The Tittle slide is the first one in the list, so its index is 0

<img src="/images/powerpoint_template_content_slide.png" alt="PowerPoint template Content slide"></img>
The Title and Content slide is the fifth one in the list, so its index is 4