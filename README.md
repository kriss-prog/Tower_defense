# 🧟 Zombie Kingdom Defense ULTRA

A strategic tower defense game built from scratch using Python and the Pygame library. Strategically place diverse defensive towers along a winding path to protect your kingdom from increasingly challenging waves of normal, fast, and heavily-armored tank zombies.

---

## 🚀 Features

* **Dynamic Wave System**: Face endless waves of zombies that grow exponentially in speed and health as the game progresses.
* **Diverse Enemy Archetypes**:
    * `Normal Zombie`: Balanced speed and health.
    * `Fast Zombie`: Quick movement but fragile.
    * `Tank Zombie`: Slow-moving but heavily armored giants.
* **4 Unique Tower Types**:
    * ⚔️ **Knight Tower**: Rapid, high-damage physical attacker with balanced range.
    * 🏹 **Archer Tower**: Exceptional firing speed with great tactical range.
    * 🔮 **Mage Tower**: Launches mystical projectiles that cause area-of-effect (AoE) blast damage.
    * 🎯 **Sniper Tower**: High-cost, slow-firing caliber designed to safely decimate high-health targets from afar.
* **Interactive Visual Shop UI**: A clean, sidebar heads-up display showcasing tower hotkeys, gold costs, and selection states.
* **Range Preview Indicator**: Hovering your mouse dynamically renders a transparent visual indicator of your selected tower's radius before placing it.
* **Persistent High Score Saving**: Tracks your record wave across play sessions using a local `highscore.txt` profile.

---

## 🎮 Controls & How to Play

The game is controlled using a combination of mouse clicks for placement/upgrades and keyboard keys for selecting towers and navigating menus.

### Mouse Controls
* 🖱️ **`Left-Click (Vasak klõps)`**: 
    * **In Game**: Place your currently selected tower on the grass area.
    * **In Menus**: Click anywhere on the start menu or game over screen to start/restart the game.
* 🖱️ **`Right-Click (Parem klõps)`**: 
    * **In Game**: Click on an existing tower to **upgrade** it. Upgrading increases its base damage, attack range, and firing rate (costs gold).

### Keyboard Hotkeys (Tower Selection)
Press the corresponding number keys on your keyboard to toggle which tower archetype you want to build from the shop panel:
* ⌨️ **`1`** — Select **Knight Tower** (Cost: 100 Gold)
* ⌨️ **`2`** — Select **Archer Tower** (Cost: 50 Gold)
* ⌨️ **`3`** — Select **Mage Tower** (Cost: 200 Gold)
* ⌨️ **`4`** — Select **Sniper Tower** (Cost: 250 Gold)

### System Controls
* ⌨️ **`ESC`**: Pause or resume the game at any time during active gameplay waves.

---

## 🛠️ Requirements & Installation

Before running the game, make sure you have Python 3.x and Pygame installed on your computer.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/kriss-prog/Tower_defense.git](https://github.com/kriss-prog/Tower_defense.git)
   cd Tower_defense
