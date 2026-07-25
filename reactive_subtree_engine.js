/**
 * Reactive Subtree Architecture v1.0
 * 
 * 1. Input Versioning: Tracks external inputs (time, auth, network) & captured versions per subtree.
 * 2. Invalidation Graph: Fine-grained graph marking ONLY dependent subtrees DIRTY on input change.
 * 3. Selective Reconstruction: Rebuilds DIRTY subtrees, reuses CLEAN subtrees.
 * 4. Memory Budgeting: LRU eviction of subtrees under memory pressure.
 */

class VersionedInput {
  constructor(id, initialValue) {
    this.id = id;
    this.value = initialValue;
    this.version = 1;
    this.subscribers = new Set(); // SubtreeNode IDs listening to this input
  }

  update(newValue) {
    if (this.value !== newValue) {
      this.value = newValue;
      this.version += 1;
      return true;
    }
    return false;
  }
}

class InputTracker {
  constructor() {
    this.inputs = new Map();
    this.activeSubtree = null;
  }

  register(id, initialValue) {
    if (!this.inputs.has(id)) {
      this.inputs.set(id, new VersionedInput(id, initialValue));
    }
    return this.inputs.get(id);
  }

  read(id) {
    const input = this.inputs.get(id);
    if (!input) throw new Error(`Input '${id}' not registered.`);

    if (this.activeSubtree) {
      this.activeSubtree.recordDependency(input.id, input.version);
      input.subscribers.add(this.activeSubtree.id);
    }
    return input.value;
  }

  update(id, newValue) {
    const input = this.inputs.get(id);
    if (input && input.update(newValue)) {
      return input;
    }
    return null;
  }
}

class SubtreeNode {
  constructor(id, renderFn) {
    this.id = id;
    this.renderFn = renderFn;
    this.dependencies = new Map(); // inputId -> capturedVersion
    this.state = 'DIRTY'; // 'CLEAN' | 'DIRTY' | 'EVICTED'
    this.cachedOutput = null;
    this.children = [];
    this.lastAccessed = Date.now();
  }

  recordDependency(inputId, version) {
    this.dependencies.set(inputId, version);
  }

  markDirty() {
    if (this.state !== 'DIRTY') {
      this.state = 'DIRTY';
    }
  }

  evict() {
    this.state = 'EVICTED';
    this.cachedOutput = null;
    this.dependencies.clear();
  }
}

class ReactiveSubtreeEngine {
  constructor(tracker, maxCachedNodes = 2) {
    this.tracker = tracker;
    this.nodes = new Map();
    this.maxCachedNodes = maxCachedNodes;
    this.lruOrder = []; // Node IDs ordered by recent usage
  }

  createSubtree(id, renderFn) {
    const node = new SubtreeNode(id, renderFn);
    this.nodes.set(id, node);
    return node;
  }

  updateInputAndInvalidate(id, newValue) {
    const updatedInput = this.tracker.update(id, newValue);
    if (!updatedInput) return 0;

    let dirtyCount = 0;
    // Fine-grained invalidation: mark ONLY subscribers dirty
    for (const nodeId of updatedInput.subscribers) {
      const node = this.nodes.get(nodeId);
      if (node) {
        node.markDirty();
        dirtyCount++;
      }
    }
    return dirtyCount;
  }

  touchLRU(nodeId) {
    this.lruOrder = this.lruOrder.filter(id => id !== nodeId);
    this.lruOrder.push(nodeId);
    const node = this.nodes.get(nodeId);
    if (node) {
      node.lastAccessed = Date.now();
    }
  }

  enforceMemoryBudget() {
    const cachedNodes = Array.from(this.nodes.values()).filter(n => n.state === 'CLEAN');
    if (cachedNodes.length > this.maxCachedNodes) {
      // Find least recently used CLEAN node
      for (const nodeId of this.lruOrder) {
        const node = this.nodes.get(nodeId);
        if (node && node.state === 'CLEAN') {
          console.log(` [MEM-BUDGET] Evicting LRU Subtree Node: '${node.id}'`);
          node.evict();
          this.lruOrder = this.lruOrder.filter(id => id !== nodeId);
          break;
        }
      }
    }
  }

  renderSubtree(nodeId) {
    const node = this.nodes.get(nodeId);
    if (!node) throw new Error(`Subtree '${nodeId}' not found.`);

    // 1. Selective Reuse: Clean cached output
    if (node.state === 'CLEAN' && node.cachedOutput !== null) {
      this.touchLRU(nodeId);
      return { output: node.cachedOutput, reconstructed: false };
    }

    // 2. Re-render DIRTY or EVICTED node
    console.log(` [RECONSTRUCT] Rebuilding Subtree Node: '${nodeId}' (State: ${node.state})`);
    
    // Clear old subscriber bindings
    for (const [inputId] of node.dependencies) {
      const input = this.tracker.inputs.get(inputId);
      if (input) input.subscribers.delete(nodeId);
    }
    node.dependencies.clear();

    // Track dependencies during rendering
    const prevActive = this.tracker.activeSubtree;
    this.tracker.activeSubtree = node;

    const output = node.renderFn(this.tracker);

    this.tracker.activeSubtree = prevActive;

    node.cachedOutput = output;
    node.state = 'CLEAN';
    this.touchLRU(nodeId);

    // Enforce Memory Budget post-render
    this.enforceMemoryBudget();

    return { output, reconstructed: true };
  }
}

// Running Self-Test
console.log("============================================================");
console.log("REACTIVE SUBTREE ENGINE: VERIFICATION DEMO");
console.log("============================================================");

const tracker = new InputTracker();
tracker.register("time:clock", "12:00 PM");
tracker.register("auth:user", "Alice");
tracker.register("network:feed", "Article 1");

const engine = new ReactiveSubtreeEngine(tracker, /* maxCachedNodes */ 2);

// Subtree 1: Auth + Clock
engine.createSubtree("HeaderSubtree", (t) => {
  const user = t.read("auth:user");
  const clock = t.read("time:clock");
  return `<header>User: ${user} | Time: ${clock}</header>`;
});

// Subtree 2: Network Feed Only
engine.createSubtree("FeedSubtree", (t) => {
  const feed = t.read("network:feed");
  return `<section>Feed: ${feed}</section>`;
});

// Subtree 3: Footer (Clock Only)
engine.createSubtree("FooterSubtree", (t) => {
  const clock = t.read("time:clock");
  return `<footer>Clock: ${clock}</footer>`;
});

console.log("\n--- Pass 1: Render All Subtrees ---");
console.log("1.", engine.renderSubtree("HeaderSubtree").output);
console.log("2.", engine.renderSubtree("FeedSubtree").output);
console.log("3.", engine.renderSubtree("FooterSubtree").output);

console.log("\n--- Pass 2: Selective Invalidation (Update network:feed) ---");
const count = engine.updateInputAndInvalidate("network:feed", "Article 2");
console.log(`Invalidated ${count} subtrees (FeedSubtree ONLY).`);

console.log("\n--- Pass 3: Re-render All Subtrees ---");
const h = engine.renderSubtree("HeaderSubtree");
console.log(`Header (Reconstructed: ${h.reconstructed}): ${h.output}`);

const f = engine.renderSubtree("FeedSubtree");
console.log(`Feed   (Reconstructed: ${f.reconstructed}): ${f.output}`);

const ft = engine.renderSubtree("FooterSubtree");
console.log(`Footer (Reconstructed: ${ft.reconstructed}): ${ft.output}`);
