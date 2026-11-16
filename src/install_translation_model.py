
import argostranslate.package

print("Checking available translation models...")

argostranslate.package.update_package_index()

packages = argostranslate.package.get_available_packages()

swedish_english = next(
    (
        p for p in packages
        if p.from_code == "sv" and p.to_code == "en"
    ),
    None
)

if swedish_english is None:
    print("Swedish-to-English model not found.")
else:
    print("Downloading Swedish-to-English model...")
    model_file = swedish_english.download()

    print("Installing model...")
    argostranslate.package.install_from_path(model_file)

    print("Swedish-to-English model installed successfully!")
