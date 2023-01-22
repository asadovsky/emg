package main

import (
	"math"
)

const smoothedWindowSize = 5  // 50ms
const trailingWindowSize = 20 // 200ms
const numWindows = 3

type StreamStats struct {
	// Computed over a sliding window of raw values.
	rawStats *SlidingWindow
	// Computed over a sliding window of smoothed values.
	smoothedStats *SlidingWindow
	// Means from `smoothedStats`.
	means *SlidingWindow
	// Variances from `smoothedStats`.
	variances *SlidingWindow
	// The first value added to `means`.
	initialMean float32
	// Current-vs-initial mean log ratios.
	meanLogRatios *SlidingWindow
}

func NewStreamStats() *StreamStats {
	return &StreamStats{
		rawStats:      NewSlidingWindow(smoothedWindowSize, true),
		smoothedStats: NewSlidingWindow(trailingWindowSize, true),
		means:         NewSlidingWindow(1, false),
		variances:     NewSlidingWindow(numWindows*trailingWindowSize+1, false),
		meanLogRatios: NewSlidingWindow(1, false),
	}
}

func (s *StreamStats) Full() bool {
	return s.rawStats.Full() && s.smoothedStats.Full() && s.means.Full() && s.variances.Full() && s.meanLogRatios.Full()
}

func (s *StreamStats) Push(value float32) {
	s.rawStats.Push(value)
	if !s.rawStats.Full() {
		return
	}
	s.smoothedStats.Push(s.rawStats.Mean())
	if !s.smoothedStats.Full() {
		return
	}
	if s.means.n == 0 {
		s.initialMean = s.smoothedStats.Mean()
	}
	s.means.Push(s.smoothedStats.Mean())
	s.variances.Push(s.smoothedStats.Variance())
	s.meanLogRatios.Push(float32(math.Log(float64(s.smoothedStats.Mean())) - math.Log(float64(s.initialMean))))
}

func (s *StreamStats) Pred() bool {
	assert(s.Full())
	if s.variances.Get(0) < 5 || s.meanLogRatios.Get(0) < 0.01 {
		return false
	}
	for i := 0; i < numWindows; i++ {
		if s.variances.Get(-(i+1)*trailingWindowSize) > 1 {
			return false
		}
	}
	return true
}
