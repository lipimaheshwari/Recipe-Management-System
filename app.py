from flask import Flask, render_template, request, redirect, url_for, flash
from pathlib import Path

app = Flask(__name__)
app.secret_key = "recipe-site-local-key"
RECIPES_FILE = Path(__file__).with_name("recipes.txt")
SEPARATOR = "=" * 40

def load_recipes():
    if not RECIPES_FILE.exists():
        RECIPES_FILE.write_text("", encoding="utf-8")
    content = RECIPES_FILE.read_text(encoding="utf-8")
    recipes = []
    for block in content.split(SEPARATOR):
        block = block.strip()
        if not block:
            continue
        recipe = {}
        for line in block.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                recipe[key.strip()] = value.strip()
        if recipe.get("Name"):
            recipes.append({
                "name": recipe.get("Name", ""),
                "category": recipe.get("Category", ""),
                "ingredients": recipe.get("Ingredients", ""),
                "steps": recipe.get("Cooking Steps", ""),
                "nutrition": recipe.get("Nutritional Info", "")
            })
    return recipes

@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").strip()
    recipes = load_recipes()
    if query:
        recipes = [r for r in recipes if query.casefold() in r["name"].casefold()]
    return render_template("index.html", recipes=recipes, query=query, total=len(load_recipes()))

@app.route("/add", methods=["POST"])
def add_recipe():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    ingredients = request.form.get("ingredients", "").strip()
    steps = request.form.get("steps", "").strip()
    nutrition = request.form.get("nutrition", "").strip()

    if not all([name, category, ingredients, steps, nutrition]):
        flash("Please fill in every field.", "error")
        return redirect(url_for("index"))

    if any(r["name"].casefold() == name.casefold() for r in load_recipes()):
        flash("A recipe with that name already exists.", "error")
        return redirect(url_for("index"))

    with RECIPES_FILE.open("a", encoding="utf-8") as file:
        if RECIPES_FILE.stat().st_size > 0:
            file.write("\n")
        file.write(
            f"Name: {name}\n"
            f"Category: {category}\n"
            f"Ingredients: {ingredients}\n"
            f"Cooking Steps: {steps}\n"
            f"Nutritional Info: {nutrition}\n"
            f"{SEPARATOR}\n"
        )

    flash(f"{name} added successfully!", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
