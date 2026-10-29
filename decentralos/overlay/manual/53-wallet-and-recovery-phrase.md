# Wallet & Recovery Phrase

Your node has its own DecentralChain wallet. It holds the node's DCC, its rewards arrive there, and its address is where you send DCC to give the node stake. The whole wallet comes from 15 words: the recovery phrase.

## The 15 words

When you start a new node, the dashboard shows 15 words picked at random for you. Together they are the key to the wallet:

- **Anyone who has them can take the funds.** Nobody from DecentralChain or DecentralOS will ever ask for them. Never type them into a website, a chat or an email.
- **They are the only way back in.** If the computer breaks or is wiped, the 15 words restore the wallet on a new one. Without them, the funds are gone for good.

Write them on paper, in order, and keep the paper somewhere safe and private. Don't store them in a photo, a notes app or a cloud drive.

## Seeing the words again

On the box's own screen, the "Your wallet" section of the dashboard has a "Show my 15 recovery words" button. It works only on the box itself: a paired phone can't show them, by design.

From a terminal, `decentralos-node seed` prints them after asking for your password.

## Restoring the wallet

To run your node with a wallet you already have, for example after replacing the computer, choose "I already have a recovery phrase" when the dashboard first starts, and type the 15 words. The node then uses the same wallet, with the same address and balance.

A computer whose node is already set up doesn't offer this. Restore onto a freshly installed DecentralOS.

## Using the wallet elsewhere

The same 15 words open the same wallet in other DecentralChain wallets. Import them into [Cubensis Connect](https://docs.decentralchain.io/en/main/09_user-guides/02_cubensis-connect.html), the DecentralChain browser wallet, on Mainnet, and you get the same address and balance as the node. That's the easiest way to send DCC out of the node's wallet, or to lease DCC to it from another wallet.

## Receiving DCC

The "Your wallet" section shows the wallet's address, which starts with `3D`, and its DCC balance. To send DCC to the node, for example to give it stake for [earning rewards](52-your-decentralchain-node.md#earning-rewards), send them to that address. DCC on the DecentralChain Testnet, or on any other blockchain, can't be sent here.

Anyone can look up the address and its balance on [DecentralScan](https://decentralscan.com/), the DecentralChain block explorer. Everything on the blockchain is public, so share the address freely, but never the 15 words.
