import os

labels_folder = r"C:\Users\Admin\Robotics\RobotArm\CameraStuff\cup_detector\cup_dataset\labels"

for root, dirs, files in os.walk(labels_folder):
    for file in files:
        if file.endswith(".txt"):
            path = os.path.join(root, file)

            with open(path, "r") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                parts = line.strip().split()

                if len(parts) >= 5:
                    parts[0] = "0"  # Change class ID to 0

                new_lines.append(" ".join(parts) + "\n")

            with open(path, "w") as f:
                f.writelines(new_lines)

print("Done!")