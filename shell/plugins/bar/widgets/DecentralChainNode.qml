import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "omarchy.decentralchain-node"

  // absent (node package not installed), unconfigured, offline, syncing, synced
  property string nodeState: "absent"
  property int height: 0
  property int peers: 0
  property int behind: 0

  function refresh() {
    if (!statusProc.running) statusProc.running = true
  }

  function openNode() {
    if (root.bar) root.bar.run("omarchy-launch-floating-terminal-with-presentation decentralos-node")
  }

  function behindText() {
    const days = Math.floor(behind / 86400)
    const hours = Math.floor((behind % 86400) / 3600)
    return days > 0 ? days + "d " + hours + "h" : hours + "h " + Math.floor((behind % 3600) / 60) + "m"
  }

  function tooltip() {
    if (nodeState === "unconfigured") return "DecentralChain node: click to set up"
    if (nodeState === "offline") return "DecentralChain node is not running"
    const detail = "block " + height + ", " + peers + (peers === 1 ? " peer" : " peers")
    if (nodeState === "syncing") return "DecentralChain node syncing, " + behindText() + " behind (" + detail + ")"
    return "DecentralChain node in sync (" + detail + ")"
  }

  visible: nodeState !== "absent"
  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  ShellIpc {
    target: "omarchy.decentralchain-node"

    function refresh(): void {
      root.broadcast("refresh")
    }
  }

  Process {
    id: statusProc
    command: ["decentralos-node", "bar"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        try {
          const status = JSON.parse(text || "{}")
          root.height = status.height || 0
          root.peers = status.peers || 0
          root.behind = status.behind || 0
          root.nodeState = status.state || "absent"
        } catch (e) {
          root.nodeState = "absent"
        }
      }
    }
  }

  Timer {
    interval: 15000
    running: true
    repeat: true
    triggeredOnStart: true
    onTriggered: root.refresh()
  }

  BarIconButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: root.nodeState === "synced" ? "" : root.nodeState === "syncing" ? "" : ""
    foreground: root.nodeState === "offline" ? root.bar.urgent : root.bar.foreground
    slotSize: Style.bar.statusSlot
    tooltipText: root.tooltip()
    onPressed: root.openNode()
  }
}
