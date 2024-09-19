
![](https://raw.githubusercontent.com/FoxySoftware/FoxySoftware.github.io/main/resource/FOXY.webp)


 ### [Web Site](https://foxysoftware.github.io)
## Modules Overview

**Foxy** is a versatile cross-platform software designed for real-time web scraping and video file extraction, offering powerful tools for capturing and processing data with precision.

### [Installation](https://foxysoftware.github.io/1.%20Installation/)


### 1. Collector Module

The **Collector Module** manages the screenshot and snapshot capture process. It allows you to configure specific images that signal various stages of a capture session:

- **Start Image**: Triggers the beginning of the capture session.
- **Optional Capture Images**: Defines additional images to be captured after the session starts.
- **End Image**: Marks the conclusion of the session.

You can also designate detection areas to monitor for changes within specific regions. If changes are detected, the system captures new images. Customizable parameters let you define the similarity threshold for "activation points" and the difference threshold for change detection. Once the end-of-session image is identified, the system automatically reanalyzes the frames to locate the start image.

The module offers an intuitive console interface to guide users through each step of the process. It supports creating multiple "Screen Sessions" within the same project, making it easy to organize captures into separate folders or groups. Each capture is managed in a messaging queue with essential metadata such as timestamps, session codes, and additional details to streamline processing in the next module.
### [More](https://foxysoftware.github.io/2.%20Collector/)
### 2. Processor Module

The **Processor Module** lets you select projects and screen sessions created in the **Collector Module** and define the areas of interest within the captured images. This step is crucial for the OCR and data extraction processes.

#### Key Features:

- **Area Labeling**: Define and assign names and groups to specific text areas for targeted data extraction.
- **Pre-Extraction Testing**: Run tests to preview extraction results and adjust settings such as thresholds and data types (e.g., string, decimal, integer).
- **Parallel Processing**: OCR and data extraction occur simultaneously with ongoing captures from the **Collector Module**, enabling efficient multi-tasking.

After processing, data is added to a RabbitMQ messaging queue, similar to the collection stage. You can then export the processed data to either a new or existing project database or a spreadsheet for further analysis.

### Data Export and Organization

Foxy dynamically structures both the database and spreadsheet outputs based on the labeled areas:

- **Database**: Each group of labeled areas is automatically mapped to a corresponding table.
- **Spreadsheet**: Data is organized hierarchically with multi-level indices, offering advanced visualization and analysis. Column names derive from the area labels, and data types are assigned based on the labeling process.
### [More](https://foxysoftware.github.io/3.%20Processor/)
