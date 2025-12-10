# Reproducibility Steps

## Versioning
- **v1.0**: Initial baseline (10k users, 2024 window).
- **SemVer**: Increment MAJOR if schema changes, MINOR if logic changes, PATCH for bugfixes.

## Regeneration
To reproduce exact dataset:
1. Ensure Python 3.9+ and requirements (`pandas`, `numpy`) are installed.
2. Run generator with fixed seed (current script uses random system time, update script to `np.random.seed(42)` for strict determinism if required).

## Size Variants
- `python generate_synthetic_data.py --size 1000` (Fast Debug)
- `python generate_synthetic_data.py --size 10000` (Production)
