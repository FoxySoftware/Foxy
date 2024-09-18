![](https://raw.githubusercontent.com/FoxySoftware/FoxySoftware.github.io/main/resource/foxy_title.png)


Foxy is a cross-platform software designed for real-time web scraping and video file scraping.

##  Modules Overview

### 1. Collector Module

The "Collector" module is responsible for capturing screenshots or snapshots. You can configure specific images to trigger various stages of the capture session:

    Start Image: Signals the beginning of the capture session.
    Optional Capture Images: Defines additional images to capture after the session has started.
    End Image: Indicates the conclusion of the session.

Additionally, you can set up a detection area to monitor for changes. The system will capture images if any alterations are detected within this defined area. Parameters can be customized to specify the similarity needed for "activation points" and the threshold difference for change detection. Once the end-of-session image is detected, the system will re-analyze the frames to find the start-of-session image.

The module features a user-friendly console interface that guides users through all processes. It also supports the creation of multiple "Screen Sessions" within the same project, facilitating the organization of captures into different groups or folders. All captures are managed in a messaging queue with metadata, including timestamp, session code, and additional data, to streamline processing in the next module.

### 2. Processor Module

The "Processor" module enables you to select projects and screen sessions created in the "Collector" module. Within this module, you need to define and label specific areas or sectors of the captured images. This labeling is crucial for the OCR and data modeling processes.

### Key features include:

    Area Labeling: Assign names and groups to text areas for extraction.
    Pre-Extraction Testing: Perform tests to preview results and adjust parameters such as thresholds and data types (string, decimal, or integer).
    Parallel Processing: OCR and data extraction can run simultaneously with ongoing captures from the "Collector" module.

Processed data is uploaded to a RabbitMQ messaging queue, similar to the collection process. The software supports exporting data to either a new or existing project database or a spreadsheet.

### Data Export and Organization

The database and spreadsheet structures are dynamically defined based on the labeled areas:

    Database: Each defined group corresponds to a table in the database.
    Spreadsheet: Data is organized hierarchically using multiple levels of indices, allowing detailed and multi-dimensional data visualization and analysis. Column names are based on area labels, and data types are determined by the labeling process.
