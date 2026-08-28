Phase status: Foundation completed; validation and integration work continuing
Project website: gardenguard.org
Project owner: Kunanon Thoonsap

1. Phase overview

Phase 1 established the initial Garden Guard brand, public website, cloud deployment pipeline and backyard-camera foundation. It also included an early Power Apps prototype to validate the proposed human-review workflow before connecting it to live detection data.

The purpose of this phase was not to deliver the complete AI platform. It was to confirm that the project could be presented publicly, deployed reliably and developed incrementally using real infrastructure.

2. Problem being explored

Backyard wildlife can damage garden beds, disturb newly planted areas and be difficult to observe consistently. Conventional deterrence products often react without explaining what animal was present, when it appeared or whether the intervention was appropriate.

Garden Guard is being developed to support a more informed and humane approach:

Observe backyard activity.

Identify likely wildlife events.

Allow a person to review the evidence.

Build a history of animal behaviour and environmental conditions.

Explore safe and humane garden-protection responses.

3. Work completed

3.1 Public website and project identity

Registered and configured the gardenguard.org domain.

Built a responsive public landing page with Next.js and Tailwind CSS.

Developed the initial Garden Guard visual identity and wildlife-focused design direction.

Added project information, roadmap content, founder details and wildlife imagery.

Iterated on the hero section and supporting visuals to improve clarity and presentation.

The public website provides a stable place to explain the project while the monitoring platform is developed separately.

3.2 AWS and Linux deployment

Provisioned an Ubuntu server on AWS Lightsail.

Packaged the website for containerised deployment with Docker Compose.

Configured Caddy as the reverse proxy.

Enabled HTTPS/TLS for the public domain.

Configured DNS through Amazon Route 53.

Deployed and maintained the application from a Linux environment.

3.3 Continuous deployment

Created a GitHub Actions workflow for automated deployment.

Configured the workflow to deploy to the Lightsail server over SSH.

Established a repeatable path from a repository update to a running containerised website.

This reduced the need for manual server updates and created a foundation for future application services.

3.4 Camera foundation

Investigated outdoor-camera options suitable for backyard monitoring.

Selected an RTSP-capable camera approach for future integration.

Installed and tested the camera for backyard viewing and recording.

Assessed camera placement, power distance and coverage of the plant-bed area.

Began reviewing recorded activity and evaluating how footage could be exported for detection testing.

The camera currently operates independently from the website and Power Apps prototype. Automated ingestion and object detection are later-phase features.

3.5 Power Apps review prototype

An early Power Apps canvas application was created to validate the detection-review experience. It includes three screens:

Dashboard — displays sample wildlife detections.

Detection Review — allows a user to inspect a selected detection.

Save Review — confirms that a review was saved successfully.

The prototype demonstrates navigation, review actions and success feedback. It currently uses hard-coded sample data and is not connected to the camera, SharePoint or a live AI-detection service.

4. Current technology stack

Area

Technology

Current use

Frontend

Next.js

Public Garden Guard website

Styling

Tailwind CSS

Responsive layout and visual system

Hosting

AWS Lightsail

Ubuntu cloud server

Containerisation

Docker Compose

Website packaging and runtime

Reverse proxy

Caddy

HTTPS and request routing

DNS

Amazon Route 53

gardenguard.org domain management

CI/CD

GitHub Actions

Automated deployment over SSH

Camera

RTSP-capable IP camera

Backyard viewing and recording

Workflow prototype

Microsoft Power Apps

Detection-review proof of concept

5. Current-state architecture

flowchart LR
    developer[Developer] --> repository[GitHub Repository]
    repository --> actions[GitHub Actions]
    actions -->|SSH deployment| lightsail[AWS Lightsail Ubuntu]
    lightsail --> compose[Docker Compose]
    compose --> caddy[Caddy HTTPS]
    caddy --> website[Next.js Website]

    visitor[Public Visitor] --> domain[gardenguard.org]
    domain --> route53[Amazon Route 53]
    route53 --> caddy

    camera[RTSP Camera] --> recordings[Camera Viewing and Recordings]

    powerApps[Power Apps Prototype] --> samples[Hard-coded Detection Samples]

The camera and Power Apps prototype are intentionally shown as separate systems. Phase 1 did not yet connect camera footage to AI detection or live dashboard records.

6. Phase 1 outcomes

Phase 1 demonstrated that Garden Guard can be treated as an evolving software product rather than only a concept. The work completed so far provides:

A public and accessible project presence.

A reproducible cloud deployment workflow.

Practical experience with AWS, Linux, containers, HTTPS and DNS.

A physical camera foundation for future computer-vision work.

A testable user-interface concept for reviewing detections.

A clearer boundary between the public website, internal MVP and future commercial platform.

7. Current limitations

The following capabilities are not presented as completed Phase 1 features:

Automated YOLO wildlife detection.

Automatic transfer of metadata or media from Linux to Microsoft 365.

A SharePoint-backed detection list and media library.

Live data inside the Power Apps dashboard.

Environmental sensor or weather-data integration.

Nightly wildlife summaries and notifications.

A production detection API, database or media-storage service.

A custom multi-user monitoring dashboard.

Automated deterrence devices or responses.

Documenting these limitations is important because it keeps the project status transparent and prevents prototype work from being described as production functionality.

8. Transition to Phase 2

The next phase will turn the Power Apps prototype into a working internal MVP using SharePoint as its initial data layer.

Planned Phase 2 work:

Create a private Garden Guard SharePoint site.

Create a Detections list for structured detection metadata.

Create a DetectionMedia document library for images and short video clips.

Replace hard-coded Power Apps records with the SharePoint connector.

Implement pending, confirmed, rejected and needs-review states.

Test the complete human-review workflow with manually added detection records.

Finalise the metadata schema before automating ingestion from the Linux server.

After the SharePoint and Power Apps workflow is validated, a later integration can use Python, YOLO and Microsoft Graph to upload detection metadata and media automatically.

9. Evidence to add

Add screenshots to an assets/phase-1/ directory and replace the placeholders below:

![Garden Guard public website](assets/phase-1/public-website.png)
![AWS deployment or container status](assets/phase-1/aws-deployment.png)
![Backyard camera view](assets/phase-1/camera-view.png)
![Power Apps detection dashboard](assets/phase-1/power-apps-dashboard.png)
![Power Apps detection review](assets/phase-1/power-apps-review.png)

Avoid publishing camera credentials, private IP addresses, SSH details, API secrets or footage containing identifiable people.

10. Key learning

The most important outcome from Phase 1 was establishing a reliable foundation before attempting the full AI workflow. Garden Guard now has deployable infrastructure, a public identity, a real camera source and a validated dashboard concept. This allows the next phases to focus on data integration and detection quality rather than building every part of the system simultaneously.
