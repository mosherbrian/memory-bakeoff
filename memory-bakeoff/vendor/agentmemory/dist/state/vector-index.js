// Pass byteOffset + byteLength explicitly so the round-trip survives
// Node's Buffer pool. Buffer.from(b64, "base64") returns a slice of a
// shared 8KB pool (poolSize), and `new Float32Array(buf.buffer)` ignores
// the slice metadata — it would mint a 2048-element view over the whole
// pool. Same risk on the encode side if the input Float32Array is itself
// a sliced view. Reported as a phantom "2048 dimensions on disk" crash
// in #455 / #469 / #584 / #587.
function float32ToBase64(arr) {
    return Buffer.from(arr.buffer, arr.byteOffset, arr.byteLength).toString("base64");
}
function base64ToFloat32(b64) {
    const buf = Buffer.from(b64, "base64");
    return new Float32Array(buf.buffer, buf.byteOffset, buf.byteLength / Float32Array.BYTES_PER_ELEMENT);
}
function cosineSimilarity(a, b) {
    if (a.length !== b.length)
        return 0;
    let dot = 0;
    let normA = 0;
    let normB = 0;
    for (let i = 0; i < a.length; i++) {
        dot += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }
    const denom = Math.sqrt(normA) * Math.sqrt(normB);
    return denom === 0 ? 0 : dot / denom;
}
export class VectorIndex {
    vectors = new Map();
    add(obsId, sessionId, embedding) {
        this.vectors.set(obsId, { embedding, sessionId });
    }
    remove(obsId) {
        this.vectors.delete(obsId);
    }
    search(query, limit = 20) {
        const results = [];
        let minScore = -Infinity;
        for (const [obsId, entry] of this.vectors) {
            const score = cosineSimilarity(query, entry.embedding);
            if (results.length < limit) {
                results.push({ obsId, sessionId: entry.sessionId, score });
                if (results.length === limit) {
                    results.sort((a, b) => a.score - b.score);
                    minScore = results[0].score;
                }
            }
            else if (score > minScore) {
                results[0] = { obsId, sessionId: entry.sessionId, score };
                results.sort((a, b) => a.score - b.score);
                minScore = results[0].score;
            }
        }
        results.sort((a, b) => b.score - a.score);
        return results;
    }
    get size() {
        return this.vectors.size;
    }
    // Walks every stored vector and returns the obsIds whose dimension
    // doesn't match `expected`, plus the set of distinct dimensions seen.
    // Used by the persistence-restore guard in src/index.ts to refuse
    // loading any index containing wrong-dimension vectors — including
    // legacy on-disk indexes written before the live-API dimension guard
    // existed (where a mid-session provider swap could mix dimensions
    // inside a single index). Empty `mismatches` plus a single-entry
    // `seenDimensions` matching `expected` is the only clean state.
    validateDimensions(expected) {
        const mismatches = [];
        const seenDimensions = new Set();
        for (const [obsId, entry] of this.vectors) {
            const dim = entry.embedding.length;
            seenDimensions.add(dim);
            if (dim !== expected) {
                mismatches.push({ obsId, dim });
            }
        }
        return { mismatches, seenDimensions };
    }
    clear() {
        this.vectors.clear();
    }
    restoreFrom(other) {
        const src = other.vectors;
        this.vectors = new Map();
        for (const [obsId, entry] of src) {
            this.vectors.set(obsId, {
                embedding: new Float32Array(entry.embedding),
                sessionId: entry.sessionId,
            });
        }
    }
    serialize() {
        const data = [];
        for (const [obsId, entry] of this.vectors) {
            data.push([
                obsId,
                {
                    embedding: float32ToBase64(entry.embedding),
                    sessionId: entry.sessionId,
                },
            ]);
        }
        return JSON.stringify(data);
    }
    static deserialize(json) {
        const idx = new VectorIndex();
        let data;
        try {
            data = JSON.parse(json);
        }
        catch {
            return idx;
        }
        if (!Array.isArray(data))
            return idx;
        for (const row of data) {
            try {
                if (!Array.isArray(row) || row.length < 2)
                    continue;
                const [obsId, entry] = row;
                if (typeof obsId !== "string" ||
                    typeof entry?.embedding !== "string" ||
                    typeof entry?.sessionId !== "string")
                    continue;
                idx.vectors.set(obsId, {
                    embedding: base64ToFloat32(entry.embedding),
                    sessionId: entry.sessionId,
                });
            }
            catch {
                continue;
            }
        }
        return idx;
    }
}
