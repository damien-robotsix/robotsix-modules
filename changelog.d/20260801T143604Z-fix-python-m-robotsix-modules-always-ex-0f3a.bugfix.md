Fix ``python -m robotsix_modules`` to forward the exit code from ``main()`` via ``sys.exit()``, instead of silently returning 0 on validation errors or parse failures.
