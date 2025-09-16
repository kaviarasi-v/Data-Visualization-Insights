from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid
import textwrap

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

df_global = None
img_files_global = []


@app.route('/', methods=['GET', 'POST'])
def index():
    global df_global, img_files_global
    data_summary = None
    dataset_name = None
    img_files = []

    if request.method == 'POST':
        file = request.files['file']
        dataset_name = file.filename
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            return "Unsupported file format. Please upload CSV or Excel."

        df_global = df  # store for later
        data_summary = f"Rows: {df.shape[0]}, Columns: {df.shape[1]}, Columns: {', '.join(df.columns)}"

        # Clear old images
        for f in os.listdir('static'):
            if f.endswith('.png'):
                os.remove(os.path.join('static', f))

        num_cols = df.select_dtypes(include='number').columns
        cat_cols = df.select_dtypes(include='object').columns

        # 1. Histogram
        if len(num_cols) > 0:
            plt.figure(figsize=(6, 4))
            df[num_cols[0]].hist(color='skyblue', edgecolor='black')
            plt.title(f'Histogram of {num_cols[0]}')
            plt.xlabel(num_cols[0])
            plt.ylabel("Frequency")
            plt.tight_layout()
            hist_path = f"static/hist_{uuid.uuid4().hex}.png"
            plt.savefig(hist_path)
            img_files.append(hist_path)
            plt.close()

        # 2. Bar Chart (Top 10 categories with counts)
        if len(cat_cols) > 0:
            plt.figure(figsize=(6, 4))
            vc = df[cat_cols[0]].value_counts().head(10)
            labels = [textwrap.shorten(str(lbl), width=15, placeholder="...") for lbl in vc.index]
            bars = plt.bar(labels, vc.values, color=sns.color_palette("Set2"))
            plt.title(f'Top 10 {cat_cols[0]}')
            plt.xticks(rotation=45, ha='right')
            plt.ylabel("Count")
            # Add value labels
            for bar in bars:
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                         str(int(bar.get_height())), ha='center', va='bottom', fontsize=8)
            plt.tight_layout()
            bar_path = f"static/bar_{uuid.uuid4().hex}.png"
            plt.savefig(bar_path)
            img_files.append(bar_path)
            plt.close()

        # 3. Correlation Heatmap
        if len(num_cols) > 1:
            plt.figure(figsize=(6, 4))
            corr = df[num_cols].corr().round(2)
            sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", cbar=True)
            plt.title("Correlation Heatmap")
            plt.tight_layout()
            heatmap_path = f"static/heatmap_{uuid.uuid4().hex}.png"
            plt.savefig(heatmap_path)
            img_files.append(heatmap_path)
            plt.close()

        # 4. Boxplot (first numeric vs first categorical)
        if len(num_cols) > 0 and len(cat_cols) > 0:
            plt.figure(figsize=(6, 4))
            df_short = df.copy()
            df_short[cat_cols[0]] = df_short[cat_cols[0]].apply(
                lambda x: textwrap.shorten(str(x), width=12, placeholder="...")
            )
            sns.boxplot(x=cat_cols[0], y=num_cols[0], data=df_short, palette="pastel")
            plt.title(f'Boxplot of {num_cols[0]} by {cat_cols[0]}')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            box_path = f"static/box_{uuid.uuid4().hex}.png"
            plt.savefig(box_path)
            img_files.append(box_path)
            plt.close()

        img_files_global = img_files

    return render_template('index.html',
                           dataset_name=dataset_name,
                           data_summary=data_summary,
                           images=img_files_global)


if __name__ == '__main__':
    app.run(debug=True)
