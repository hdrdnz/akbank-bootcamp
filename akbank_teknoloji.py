"""

**1.Veri Yükleme ve Hazırlık**

**Akbank Teknoloji Okuryazarlığı Proje Ödevi**
"""

import pandas as pd

csv_user =pd.read_csv("/content/sample_data/users.csv")
csv_transactions =pd.read_csv("/content/sample_data/transactions.csv")

csv_user["Per Capita Income - Zipcode"] = csv_user["Per Capita Income - Zipcode"].astype(str).str.replace(r'^\s*\$\s*', '', regex=True).str.strip();

csv_user["Total Debt"] = (
        csv_user["Total Debt"].astype(str)
        .str.replace(r'^\$', '', regex=True)
        .str.replace(',', '', regex=False)
        .str.strip()
    )
csv_user["Total Debt"] = pd.to_numeric(csv_user["Total Debt"], errors='coerce').astype('float64')

csv_user["Yearly Income - Person"] = (
        csv_user["Yearly Income - Person"].astype(str)
        .str.replace(r'[\$,]', '', regex=True)
        .str.strip()
    )
csv_user["Yearly Income - Person"] = pd.to_numeric(csv_user["Yearly Income - Person"], errors='coerce').astype('float64')
csv_user["Per Capita Income - Zipcode"] = pd.to_numeric(
        csv_user["Per Capita Income - Zipcode"], errors='coerce'
).astype('float64')

#birleştirme işlemi
merged_df =csv_user.merge(csv_transactions,on="User")

"""**2. En Fazla Harcama Yapılan Şehirler**"""

import matplotlib.pyplot as plt

amountCities =merged_df.groupby("Merchant City")["Amount"].sum()
amountCities=amountCities.sort_values(ascending=False)

#En fazla harcama yapılan ilk 10 şehir
print(amountCities.head(10))

print("-------------------------------------")
top10_cities = amountCities.head(10)
plt.figure(figsize=(10, 6))
bars = plt.bar(top10_cities.index, top10_cities.values, color="skyblue", edgecolor="black")
plt.title("En Fazla Harcama Yapılan Şehirler", fontsize=16, fontweight='bold')
plt.ylabel("Harcama Miktarı", fontsize=12)
plt.xlabel("Şehirler", fontsize=12)

plt.xticks(rotation=30, ha='right', fontsize=10)
plt.yticks(fontsize=10)


plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.bar_label(bars, fmt="%.0f", padding=3, fontsize=9, fontweight="bold")

plt.tight_layout()
plt.show()

"""En fazla harcamanın yapıldığı şehir **La Verne** olmuştur. Diğer şehirlerle karşılaştırıldığında harcama tutarları birbirine yakın değildir; şehirler arasında belirgin farklılıklar göze çarpmaktadır.

**3. Saatlik Harcama Dağılımı**
"""

from matplotlib.ticker import FuncFormatter

# Her saate karşılık gelen toplam harcama
merged_df["Hour"]=merged_df["Time"].str[:2]
hourlyAmounts =merged_df.groupby("Hour")["Amount"].sum()



def k_format(x, pos):
    """Y eksenini K formatında yazdırır"""
    if x >= 1_000_000:
        return f'{x/1_000_000:.1f}M'
    elif x >= 1000:
        return f'{int(x/1000)}K'
    else:
        return int(x)

plt.figure(figsize=(12, 6))
plt.plot(hourlyAmounts.index, hourlyAmounts.values,
         marker='o', markersize=6, linewidth=2, color='#1f77b4')

plt.title("Saatlere Göre Toplam Harcama", fontsize=18, fontweight='bold', color='#333333')
plt.xlabel("Saat", fontsize=14)
plt.ylabel("Toplam Harcama", fontsize=14)

plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.xticks(rotation=45, ha='right', fontsize=11)
plt.yticks(fontsize=11)

# Y eksenini K formatına çevir
plt.gca().yaxis.set_major_formatter(FuncFormatter(k_format))

# Min & Max noktaları
max_idx = hourlyAmounts.idxmax()
min_idx = hourlyAmounts.idxmin()
max_val = hourlyAmounts[max_idx]
min_val = hourlyAmounts[min_idx]

plt.scatter(max_idx, max_val, color='red', s=80, zorder=5)
plt.scatter(min_idx, min_val, color='green', s=80, zorder=5)

plt.annotate(f'Max: {max_val:,.0f}',
             xy=(max_idx, max_val),
             xytext=(max_idx, max_val + max_val*0.15),
             arrowprops=dict(facecolor='red', arrowstyle='->'),
             fontsize=12, fontweight='bold', color='red', ha='center')

plt.annotate(f'Min: {min_val:,.0f}',
             xy=(min_idx, min_val),
             xytext=(min_idx, min_val + max_val*0.1),
             arrowprops=dict(facecolor='green', arrowstyle='->'),
             fontsize=12, fontweight='bold', color='green', ha='center')

plt.tight_layout()
plt.show()

"""Saatlere göre toplam harcama dağılımında, en fazla harcamanın 06:00 saatinde, en az harcamanın ise 01:00 saatinde gerçekleştiği görülmektedir. Genel olarak harcamalar, özellikle 05:00–07:00 saatleri arasında belirgin bir artış göstermektedir.

**4. Cinsiyete Göre Harcama**
"""

import numpy as np

genderAmount = merged_df.groupby("Gender")["Amount"].sum()

def kfmt_num(x):
    if x >= 1_000_000:
        return f'{x/1_000_000:.1f}M'
    elif x >= 1_000:
        return f'{x/1_000:.0f}K'
    else:
        return f'{x:.0f}'


def autopct_format(values):
    total = values.sum()
    def inner(pct):
        val = pct * total / 100.0
        return f'{pct:.1f}%\n{kfmt_num(val)}'
    return inner

labels = genderAmount.index
sizes  = genderAmount.values

explode = np.where(sizes == sizes.max(), 0.05, 0.0)

fig, ax = plt.subplots(figsize=(6.5, 6.5))
wedges, texts, autotexts = ax.pie(
    sizes,
    labels=labels,
    autopct=autopct_format(genderAmount),
    startangle=90,
    explode=explode,
    counterclock=False,
    colors=['pink', 'skyblue'] if len(sizes)==2 else None
)

plt.setp(autotexts, size=10, weight='bold')

ax.set_title("Cinsiyete Göre Toplam Harcama", fontsize=14, fontweight='bold')
ax.axis('equal')
plt.tight_layout()
plt.show()

"""Cinsiyete göre harcama dağılımında belirgin bir oran farkı bulunmamaktadır; ancak kadınların toplam harcama miktarının erkeklere kıyasla biraz daha yüksek olduğu görülmektedir.

**5. Gelire Göre Harcama**
"""

#- Yearly Income - Person kolonundaki $ işaretini kaldırarak sayıya çevirin. : en başta işaret kaldırma işlemini gerçekleştirdim.
merged_df["Yearly Income - Person"] = pd.to_numeric(merged_df["Yearly Income - Person"], errors="coerce")
merged_df["Amount"] = pd.to_numeric(merged_df["Amount"], errors="coerce")

def kfmt(x, pos):
    if x >= 1_000_000: return f'{x/1_000_000:.1f}M'
    if x >= 1_000:     return f'{x/1000:.0f}K'
    return f'{x:.0f}'

plt.figure(figsize=(9,6))
plt.scatter(
    merged_df['Yearly Income - Person'],   # X: Yıllık Gelir
    merged_df['Amount'],                   # Y: Harcama Miktarı
    s=30, alpha=0.6, color='seagreen', edgecolors='k', linewidths=0.3, label='Kayıt'
)

plt.title("Yıllık Gelir ve Harcama Miktarı", fontsize=16, fontweight='bold')
plt.xlabel("Yıllık Gelir", fontsize=12)
plt.ylabel("Harcama Miktarı", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)

ax = plt.gca()
ax.xaxis.set_major_formatter(FuncFormatter(kfmt))
ax.yaxis.set_major_formatter(FuncFormatter(kfmt))

plt.legend()
plt.tight_layout()
plt.show()

"""Yıllık gelir ve harcama miktarı dağılımına göre, 0–100K gelir aralığında bulunan kişilerin harcama miktarlarının diğer gruplara kıyasla daha yüksek olduğu görülmektedir. Gelir seviyesinin artmasıyla birlikte harcama miktarlarında ise azalma eğilimi gözlemlenmektedir.

**3.AŞAMA CHAT ÖRNEK GRAFİK**
"""

amountMonths =merged_df.groupby("Month")["Amount"].sum()

# Bar grafiği çiz
plt.figure(figsize=(10, 6))
bars = plt.bar(amountMonths.index, amountMonths.values, color="orange", edgecolor="black")

plt.title("Aylık Harcama Miktarları", fontsize=16, fontweight='bold')
plt.ylabel("Harcama Miktarı", fontsize=12)
plt.xlabel("Aylar", fontsize=12)

plt.xticks(rotation=30, ha='right', fontsize=10)
plt.yticks(fontsize=10)

plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.bar_label(bars, fmt="%.0f", padding=3, fontsize=9, fontweight="bold")

plt.tight_layout()
plt.show()