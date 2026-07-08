# Adaptive Multi-Modal SLAM με Uncertainty-Aware Sensor Fusion

Ερευνητικό αποθετήριο για προσαρμοστική σύντηξη ετερογενών αισθητήρων σε SLAM, με ρητή μοντελοποίηση αβεβαιότητας, αξιοπιστίας, υποβάθμισης και πιθανών αποτυχιών αντίληψης.

## Κεντρικό ερευνητικό ερώτημα

Πώς μπορεί ένα σύστημα SLAM να συντήκει δυναμικά κάμερες, IMU, LiDAR και RGB-D δεδομένα, όταν η αξιοπιστία κάθε αισθητήρα μεταβάλλεται στο χρόνο;

## Τι έχει υλοποιηθεί

- Βασική αφαίρεση αισθητήρων με timestamp, covariance και reliability score.
- Προσαρμοστικά βάρη σύντηξης μέσω pseudo-precision.
- Adaptive covariance scaling.
- Mahalanobis gating για innovation consistency.
- NEES/NIS, trace covariance, log-determinant και entropy proxies.
- ATE/RPE utilities.
- Deterministic synthetic demo GIF script.

## Πρωτότυπα / scaffolds

- EKF backend scaffold.
- Factor graph scaffold.
- Loop closure scaffold.
- Sparse/trajectory/occupancy/semantic mapping scaffolds.
- ROS2 και dataset loaders ως μελλοντικές επεκτάσεις.

## Περιορισμοί

Δεν αναφέρονται πραγματικά benchmark αποτελέσματα χωρίς reproducible configs, metrics και dataset manifests. Το synthetic demo είναι μόνο για επίδειξη λειτουργίας του λογισμικού και όχι επιστημονικό αποτέλεσμα.
