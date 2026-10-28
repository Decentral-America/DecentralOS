# Your DecentralChain Node

Every DecentralOS computer runs a DecentralChain node. The node keeps a full copy of the DecentralChain blockchain, checks every new block and transaction, and passes them on to the rest of the network. With enough DCC behind it, it also takes part in creating new blocks and earns rewards for doing so.

You don't need to know any of that to run one. The node starts by itself every time the computer starts, keeps itself up to date, and tells you on the [dashboard](54-node-dashboard.md) if anything needs your attention.

## Starting your node for the first time

The first time DecentralOS starts, the dashboard fills the screen and offers two ways in:

- **Start my node**: the dashboard shows 15 recovery words for a brand-new wallet. Write them on paper, in order, tick "I have written down all 15 words and stored them safely", and press the button.
- **I already have a recovery phrase**: type the 15 words of a wallet you already have, and press "Use this phrase and start my node". Use this to move your node to a new computer, or to run it with a wallet you already use.

Read [Wallet & Recovery Phrase](53-wallet-and-recovery-phrase.md) before you choose: those 15 words are the only way back into the wallet.

You can do this from your phone instead of the box's own screen: see [Phone Pairing](55-phone-pairing.md).

## Catching up with the network

A new node starts at the very first block and downloads every block since then. The first time, this takes many hours. Leave the computer on and connected; there is nothing else to do. The dashboard shows how far along it is, and the node icon in the top bar shows whether it is in sync, catching up, or stopped. Hover over the icon for the current block and the number of other nodes it is connected to; click it to open the dashboard.

Once the node has caught up, it stays in sync on its own, block by block.

## Keeping it running

A node is only useful while it is online, so DecentralOS behaves like an appliance rather than a laptop:

- **It never sleeps.** Suspend and hibernate are turned off, and the screen never blanks or locks, so the dashboard stays visible.
- **It comes back after a power cut.** The owner account signs in automatically at every start, which brings the dashboard back on screen. To turn that off, create the file `/etc/decentralos/no-autologin` (for example with `sudo touch /etc/decentralos/no-autologin`).
- **It restarts itself.** If the node stops, it is started again within a minute. If the dashboard still says "Your node has stopped" after that, unplug the computer, wait ten seconds and plug it back in.
- **It stays reachable.** Port 6868 is open so other nodes can connect to yours. The dashboard (port 6870) answers only on your home or office network, never on the internet.

Leave at least 10 GB of storage free. The dashboard warns you when the disk is nearly full, because the blockchain keeps growing.

## Updates

Once a day, at a random time, the computer checks the DecentralOS package repository for a newer DecentralChain node and installs it. It updates only the node, so it can never start a full system upgrade on its own. Updates to the rest of DecentralOS work as described in [Updates](30-updates.md).

## Earning rewards

A node takes part in creating blocks once it has at least 1,000 DCC behind it. That stake can be DCC held in the node's own wallet, DCC that other people lease to it, or both. Leased DCC never leave their owners' wallets: they only count towards your node, and their owners can take them back at any time.

The "Earning rewards" section of the dashboard shows how much stake your node has. New stake counts after about 1,000 blocks, roughly 17 hours. Rewards arrive in the node's wallet.

## From a terminal

The dashboard is the everyday view. For support, the `decentralos-node` command gives the same information in a terminal:

| Command | What it does |
|---|---|
| `decentralos-node open` | Open the dashboard |
| `decentralos-node status` | Show whether the node is running and in sync, its current block, peers and wallet address |
| `decentralos-node logs` | Follow the node's log (`Ctrl + C` to stop) |
| `decentralos-node seed` | Print the wallet's 15 recovery words (asks for your password) |

## When something is wrong

The dashboard lists anything that needs attention at the top, each with what to do about it. The common ones:

| Message | What to do |
|---|---|
| This box is not connected to a network | Plug in a cable from your router, or join Wi-Fi from the Network section of the dashboard |
| No internet connection | Check that your router is online, then wait a minute |
| Not connected to any other nodes yet | Normal for the first few minutes; if it lasts longer than half an hour, restart your router |
| Your node has stopped | Wait a minute; if it stays, unplug the computer for ten seconds and plug it back in |
| Storage is almost full | Contact support before the node runs out of room |
