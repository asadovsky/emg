package main

type SlidingWindow struct {
	windowSize int
	trackStats bool
	values     []float32
	i          int
	n          int
	mean       float32
	variance   float32
}

func NewSlidingWindow(windowSize int, trackStats bool) *SlidingWindow {
	return &SlidingWindow{
		windowSize: windowSize,
		trackStats: trackStats,
		values:     make([]float32, windowSize),
	}
}

func (s *SlidingWindow) Size() int {
	return s.n
}

func (s *SlidingWindow) Full() bool {
	return s.n == s.windowSize
}

func (s *SlidingWindow) Get(i int) float32 {
	assert(i <= 0 && i > -s.n)
	return s.values[(s.i+i+s.windowSize)%s.windowSize]
}

func (s *SlidingWindow) Mean() float32 {
	return s.mean
}

func (s *SlidingWindow) Variance() float32 {
	return s.variance
}

func (s *SlidingWindow) Push(value float32) {
	s.i = (s.i + 1) % s.windowSize
	if !s.trackStats {
		if !s.Full() {
			s.n++
		}
	} else {
		oldMean := s.mean
		if !s.Full() {
			// Welford's algorithm.
			s.n++
			s.mean += (value - s.mean) / float32(s.n)
			s.variance += (value - s.mean) * (value - oldMean)
			if s.Full() {
				s.variance /= float32(s.n - 1)
			}
		} else {
			// https://jonisalonen.com/2014/efficient-and-accurate-rolling-standard-deviation/
			oldValue := s.Get(0)
			s.mean += (value - oldValue) / float32(s.n)
			s.variance += (value - oldValue) * (value - s.mean + oldValue - oldMean) / float32(s.n-1)
		}
	}
	s.values[s.i] = value
}
