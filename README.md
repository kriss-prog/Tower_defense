# 🧟 Zombie Kingdom Defense ULTRA

A strategic, action-packed tower defense game built from scratch using Python and the Pygame library. Defend your kingdom path against endless, scaling waves of zombies, and prepare your defenses for the massive Boss fights that arrive every 5 waves!

---

## 🚀 Features

* **Dynamic Scaling System**: Zombies dynamically gain more health and movement speed with each passing wave, keeping the gameplay challenging.
* **Every 5 Waves - BOSS WAVE**: Face a colossal Boss Zombie equipped with 10x normal health and a golden crown. The Boss doesn't come alone—a tactical wave of smaller minions runs alongside him!
* **Dynamic Visual Models**: Built entirely with code-rendered graphics. Watch your towers dynamically rotate, aim, and track targets in real-time.
* **4 Specialized Tower Types**:
    * ⚔️ **Knight Tower** ($100 Gold): High-damage physical attacker with balanced range.
    * 🏹 **Archer Tower** ($100 Gold): Rapid firing speed, perfect for cleaning up fast moving targets.
    * 🔮 **Mage Tower** ($200 Gold): Deals powerful Area-of-Effect (AoE) splash damage with magical bursts.
    * 🎯 **Sniper Tower** ($500 Gold): Long-range caliber designed specifically to melt down high-health Bosses and Tanks.
* **Refund/Sell Subsystem**: Instantly enter Sell Mode to remove existing towers and recover **75% of their total value** in gold.
* **Persistent High Scores**: Tracks and saves your highest wave locally using a `highscore.txt` profile.

---

## 🎮 Controls & How to Play

Manage your economy carefully, choose the right towers for the job, and remember to upgrade your frontline defenses!

### Mouse Actions
* 🖱️ **`Left-Click`**: 
    * *In Game Area*: Place your currently selected tower type on the grass.
    * *In Sell Mode*: Click on a tower to instantly sell it for a 75% refund.
    * *In Menus*: Click anywhere to start or restart the game.
* 🖱️ **`Right-Click`**: Click on an already placed tower to **Upgrade** it. Upgrades permanently increase its damage, range, and attack speed.

### Keyboard Shortcuts
* ⌨️ **`1`** — Select **Knight Tower**
* ⌨️ **`2`** — Select **Archer Tower**
* ⌨️ **`3`** — Select **Mage Tower**
* ⌨️ **`4`** — Select **Sniper Tower**
* ⌨️ **`S`** — Toggle **Sell Mode** on / off
* ⌨️ **`ESC`** — Pause / Resume the game

---

## 🛠️ Installation & Setup

Make sure you have Python 3.x and Pygame installed on your local machine before running the game.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/kriss-prog/Tower_defense.git](https://github.com/kriss-prog/Tower_defense.git)
   cd Tower_defense
