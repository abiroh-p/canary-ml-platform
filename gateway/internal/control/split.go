package control

import (
	"encoding/json"
	"errors"
	"log/slog"
	"net/http"
)

var ErrInvalidWeight = errors.New("canary weight must be between 0 and 100")

type splitRequest struct {
	CanaryWeight int32 `json:"canary_weight"`
}

// AdminHandler returns an http.Handler for the admin API, calling back
// into the given SplitState. Kept separate from SplitState itself so
// the state type has no HTTP dependency — testable without a server.
func AdminHandler(state *SplitState) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("POST /admin/traffic-split", func(w http.ResponseWriter, r *http.Request) {
		var req splitRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "invalid request body", http.StatusBadRequest)
			return
		}

		if err := state.SetCanaryWeight(req.CanaryWeight); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		slog.Info("traffic split updated", "canary_weight", req.CanaryWeight)
		w.WriteHeader(http.StatusOK)
	})

	mux.HandleFunc("GET /admin/traffic-split", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(splitRequest{CanaryWeight: state.CanaryWeight()})
	})

	return mux
}