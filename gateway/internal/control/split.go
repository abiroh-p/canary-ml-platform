// Package control implements the gateway's control plane: the current
// canary traffic split (in memory) and the admin API to change it.
package control

import "sync/atomic"

// SplitState holds the current canary traffic percentage (0-100),
// safe for concurrent reads (data plane) and rare writes (control plane).
type SplitState struct {
	canaryWeight atomic.Int32
}

func NewSplitState() *SplitState {
	s := &SplitState{}
	s.canaryWeight.Store(0)
	return s
}

func (s *SplitState) CanaryWeight() int32 {
	return s.canaryWeight.Load()
}

func (s *SplitState) SetCanaryWeight(weight int32) error {
	if weight < 0 || weight > 100 {
		return ErrInvalidWeight
	}
	s.canaryWeight.Store(weight)
	return nil
}
