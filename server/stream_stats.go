package main

import (
	"math"
)

const statsWindowSize = 20    // 200ms
const slidingWindowSize = 300 // 3s

type StreamStats struct {
	// Computed over a sliding window of raw values.
	stats *SlidingWindow
	// Means and variances from `stats`.
	means     *SlidingWindow
	variances *SlidingWindow
	// Current-vs-recent mean and variance log ratios.
	meanLogRatios     *SlidingWindow
	varianceLogRatios *SlidingWindow
}

func NewStreamStats() *StreamStats {
	return &StreamStats{
		stats:             NewSlidingWindow(statsWindowSize, true),
		means:             NewSlidingWindow(slidingWindowSize, false),
		variances:         NewSlidingWindow(slidingWindowSize, false),
		meanLogRatios:     NewSlidingWindow(slidingWindowSize, false),
		varianceLogRatios: NewSlidingWindow(slidingWindowSize, false),
	}
}

func (s *StreamStats) Full() bool {
	return s.stats.Full() && s.means.Full() && s.variances.Full() && s.meanLogRatios.Full() && s.varianceLogRatios.Full()
}

func (s *StreamStats) Push(value float32) {
	s.stats.Push(value)
	if !s.stats.Full() {
		return
	}
	mean, variance := s.stats.Mean(), s.stats.Variance()
	s.means.Push(mean)
	s.variances.Push(variance)
	i := -100 // -1s
	if s.means.Size() <= -i {
		return
	}
	s.meanLogRatios.Push(float32(math.Log(float64(mean)) - math.Log(float64(s.means.Get(i)))))
	s.varianceLogRatios.Push(float32(math.Log(float64(variance)) - math.Log(float64(s.variances.Get(i)))))
}

func (s *StreamStats) Pred() bool {
	assert(s.Full())
	// Mean spike at 0s.
	if s.meanLogRatios.Get(0) < 0.015 {
		return false
	}
	// Mean dip in [-1s, 0s].
	i := 0
	for ; ; i-- {
		if i < -100 {
			return false
		}
		if s.meanLogRatios.Get(i) < -0.015 {
			break
		}
	}
	// No mean spike in [-2s, dip].
	for ; i > -200; i-- {
		if s.meanLogRatios.Get(i) > 0.015 {
			return false
		}
	}
	return true
}
