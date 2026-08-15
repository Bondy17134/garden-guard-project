# Garden-animal training dataset

This dataset trains two species-specific detection classes:

1. `bush_turkey`
2. `possum`

Create this structure. Images and labels stay out of Git because they can become large and may contain private camera footage.

```text
dataset/
  images/
    train/
    val/
    test/       # optional
  labels/
    train/
    val/
    test/       # optional
  garden_animals.yaml
```

Use clean, unannotated camera images. Include day and infrared-night frames, varied distances and angles, and difficult negatives such as empty garden scenes, plants moving in wind, and other birds.

Label every visible target with a bounding box. Export annotations in **YOLO Detection** format. Each image needs a matching text file in the equivalent `labels/` folder. For example, this label file describes one bush turkey and one possum:

```text
0 0.500000 0.600000 0.300000 0.250000
1 0.200000 0.400000 0.120000 0.180000
```

Each row is `class_id x_center y_center width height`; all four coordinates are normalised to 0–1. Empty images need an empty matching label file.

Start with an 80%/20% train/validation split. Aim for at least 300 labelled examples per species, including a substantial number of night images; 1,000+ per species will be much more robust. Keep a separate test set that you do not use to choose settings.

Do not label an animal as a `bush_turkey` or `possum` unless you are confident of the species. Incorrect labels teach the model the wrong pattern.
