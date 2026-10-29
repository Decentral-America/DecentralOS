# Phone Pairing

You don't need a screen or keyboard on the box to run a node. Pair your phone, and it opens the [dashboard](54-node-dashboard.md) in its web browser: you can finish setup and check on the node from there.

## Pairing a phone

1. Make sure the phone is on the same Wi-Fi network as the DecentralOS computer.
2. On the dashboard, find "Use your phone" and scan its QR code with the phone's camera.
3. The dashboard opens in the phone's browser.

The phone stays paired: the next time, open the same page and it goes straight to the dashboard. Pair as many phones as you like.

A paired phone works only on your home or office network. The dashboard never answers from the internet, so it can't be reached from outside. Anyone who opens it without pairing sees "Scan the QR code on your DecentralOS screen to connect this device."

## What a phone can and can't do

A paired phone sees everything the dashboard shows, and can start the node during first-time setup. Two things stay on the box's own screen, on purpose:

- **Showing the 15 recovery words.** A phone can be lost or looked over; the words never leave the box.
- **Changing the Wi-Fi network**, except during first-time setup through the setup network below.

## Setting up without a keyboard or cable

A brand-new DecentralOS computer with no network cable and no saved Wi-Fi starts its own setup Wi-Fi network, so you can connect it from your phone:

1. On your phone, join the Wi-Fi network **DecentralOS-Setup** with the password **decentralchain**. The dashboard's "Connect this box" section also shows a QR code that joins it in one scan.
2. A page opens by itself. If it doesn't, open a browser on the phone and go to any address.
3. Choose your home Wi-Fi, enter its password and press "Join Wi-Fi". Joining takes about half a minute.
4. The setup network then switches off. Put your phone back on your home Wi-Fi and open the link the page showed you. It uses the name `decentralos.local`, so it keeps working even if the box's address changes.

If the box can't join your Wi-Fi, for example because of a mistyped password, it forgets that network and the setup network comes back. Join it again and retry.

The setup network's password is the same on every DecentralOS computer, so finish setup soon after you start it. The setup network turns off for good once the box has a cable or a saved Wi-Fi.

## Unpairing every phone

To revoke every paired phone, for example after losing one, make a new pairing code from a terminal on the box:

```bash
sudo rm /var/lib/decentralchain/dashboard-token
sudo systemctl restart decentralos-dashboard
```

The dashboard then shows a new QR code, and phones paired before have to scan it again.
