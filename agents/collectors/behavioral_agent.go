package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"syscall"
	"time"
	"unsafe"

	"github.com/go-redis/redis/v8"
	"github.com/gorilla/websocket"
	"github.com/shirou/gopsutil/v3/cpu"
	"github.com/shirou/gopsutil/v3/mem"
	"github.com/shirou/gopsutil/v3/process"
)

// Event represents a behavioral event
type Event struct {
	UserID      string                 `json:"user_id"`
	EventType   string                 `json:"event_type"`
	Timestamp   time.Time              `json:"timestamp"`
	SourceIP    string                 `json:"source_ip"`
	UserAgent   string                 `json:"user_agent"`
	EventData   map[string]interface{} `json:"event_data"`
	ProcessedAt time.Time              `json:"processed_at"`
}

// KeystrokeEvent represents keystroke dynamics data
type KeystrokeEvent struct {
	KeyCode     int     `json:"key_code"`
	DwellTime   float64 `json:"dwell_time"`
	FlightTime  float64 `json:"flight_time"`
	Pressure    float64 `json:"pressure"`
	TypingSpeed float64 `json:"typing_speed"`
	Sequence    string  `json:"sequence"`
}

// MouseEvent represents mouse movement data
type MouseEvent struct {
	X            int     `json:"x"`
	Y            int     `json:"y"`
	Velocity     float64 `json:"velocity"`
	Acceleration float64 `json:"acceleration"`
	ClickType    string  `json:"click_type"`
	Pressure     float64 `json:"pressure"`
	Trajectory   string  `json:"trajectory"`
}

// FileAccessEvent represents file system access
type FileAccessEvent struct {
	FilePath     string    `json:"file_path"`
	AccessType   string    `json:"access_type"`
	FileSize     int64     `json:"file_size"`
	FileType     string    `json:"file_type"`
	ProcessName  string    `json:"process_name"`
	AccessTime   time.Time `json:"access_time"`
	Permissions  string    `json:"permissions"`
}

// NetworkEvent represents network activity
type NetworkEvent struct {
	DestinationIP   string `json:"destination_ip"`
	DestinationPort int    `json:"destination_port"`
	Protocol        string `json:"protocol"`
	DataVolume      int64  `json:"data_volume"`
	Domain          string `json:"domain"`
	RequestType     string `json:"request_type"`
	UserAgent       string `json:"user_agent"`
}

// BehavioralAgent collects behavioral data
type BehavioralAgent struct {
	userID      string
	redisClient *redis.Client
	wsConn      *websocket.Conn
	config      *AgentConfig
	ctx         context.Context
	cancel      context.CancelFunc
}

// AgentConfig holds agent configuration
type AgentConfig struct {
	RedisAddr     string `json:"redis_addr"`
	RedisPassword string `json:"redis_password"`
	RedisDB       int    `json:"redis_db"`
	ServerURL     string `json:"server_url"`
	CollectKeystrokes bool `json:"collect_keystrokes"`
	CollectMouse      bool `json:"collect_mouse"`
	CollectFiles      bool `json:"collect_files"`
	CollectNetwork    bool `json:"collect_network"`
	SampleRate        int  `json:"sample_rate"` // Events per second
}

// NewBehavioralAgent creates a new behavioral agent
func NewBehavioralAgent(userID string, config *AgentConfig) *BehavioralAgent {
	ctx, cancel := context.WithCancel(context.Background())
	
	rdb := redis.NewClient(&redis.Options{
		Addr:     config.RedisAddr,
		Password: config.RedisPassword,
		DB:       config.RedisDB,
	})

	return &BehavioralAgent{
		userID:      userID,
		redisClient: rdb,
		config:      config,
		ctx:         ctx,
		cancel:      cancel,
	}
}

// Start begins data collection
func (ba *BehavioralAgent) Start() error {
	log.Printf("Starting behavioral agent for user: %s", ba.userID)

	// Connect to WebSocket server
	if err := ba.connectWebSocket(); err != nil {
		return fmt.Errorf("failed to connect to WebSocket: %v", err)
	}

	// Start collection goroutines
	if ba.config.CollectKeystrokes {
		go ba.collectKeystrokeData()
	}
	if ba.config.CollectMouse {
		go ba.collectMouseData()
	}
	if ba.config.CollectFiles {
		go ba.collectFileAccessData()
	}
	if ba.config.CollectNetwork {
		go ba.collectNetworkData()
	}

	// Start system monitoring
	go ba.collectSystemData()

	// Keep agent running
	<-ba.ctx.Done()
	return nil
}

// Stop stops the agent
func (ba *BehavioralAgent) Stop() {
	log.Printf("Stopping behavioral agent for user: %s", ba.userID)
	ba.cancel()
	if ba.wsConn != nil {
		ba.wsConn.Close()
	}
	ba.redisClient.Close()
}

// connectWebSocket establishes WebSocket connection
func (ba *BehavioralAgent) connectWebSocket() error {
	dialer := websocket.DefaultDialer
	conn, _, err := dialer.Dial(ba.config.ServerURL+"/ws/agent/"+ba.userID, nil)
	if err != nil {
		return err
	}
	ba.wsConn = conn
	return nil
}

// collectKeystrokeData collects keystroke dynamics (placeholder)
func (ba *BehavioralAgent) collectKeystrokeData() {
	ticker := time.NewTicker(time.Second / time.Duration(ba.config.SampleRate))
	defer ticker.Stop()

	var lastKeyTime time.Time
	var keySequence []int

	for {
		select {
		case <-ba.ctx.Done():
			return
		case <-ticker.C:
			// Simulate keystroke data collection
			// In production, this would hook into the OS keyboard events
			keystrokeEvent := ba.generateKeystrokeEvent(&lastKeyTime, &keySequence)
			if keystrokeEvent != nil {
				ba.sendEvent("keystroke", keystrokeEvent)
			}
		}
	}
}

// collectMouseData collects mouse movement data (placeholder)
func (ba *BehavioralAgent) collectMouseData() {
	ticker := time.NewTicker(time.Millisecond * 100) // 10 Hz
	defer ticker.Stop()

	var lastX, lastY int
	var lastTime time.Time

	for {
		select {
		case <-ba.ctx.Done():
			return
		case <-ticker.C:
			// Simulate mouse data collection
			mouseEvent := ba.generateMouseEvent(&lastX, &lastY, &lastTime)
			if mouseEvent != nil {
				ba.sendEvent("mouse_movement", mouseEvent)
			}
		}
	}
}

// collectFileAccessData monitors file system access
func (ba *BehavioralAgent) collectFileAccessData() {
	ticker := time.NewTicker(time.Second * 5) // Every 5 seconds
	defer ticker.Stop()

	for {
		select {
		case <-ba.ctx.Done():
			return
		case <-ticker.C:
			// Get current process file handles
			processes, err := process.Processes()
			if err != nil {
				continue
			}

			for _, proc := range processes {
				// Check if process belongs to current user
				if ba.isUserProcess(proc) {
					fileEvents := ba.getProcessFileAccess(proc)
					for _, event := range fileEvents {
						ba.sendEvent("file_access", event)
					}
				}
			}
		}
	}
}

// collectNetworkData monitors network activity
func (ba *BehavioralAgent) collectNetworkData() {
	ticker := time.NewTicker(time.Second * 10) // Every 10 seconds
	defer ticker.Stop()

	for {
		select {
		case <-ba.ctx.Done():
			return
		case <-ticker.C:
			// Collect network statistics
			networkEvents := ba.getNetworkActivity()
			for _, event := range networkEvents {
				ba.sendEvent("network_request", event)
			}
		}
	}
}

// collectSystemData monitors system-level activity
func (ba *BehavioralAgent) collectSystemData() {
	ticker := time.NewTicker(time.Second * 30) // Every 30 seconds
	defer ticker.Stop()

	for {
		select {
		case <-ba.ctx.Done():
			return
		case <-ticker.C:
			// Collect system metrics
			cpuPercent, _ := cpu.Percent(time.Second, false)
			memStats, _ := mem.VirtualMemory()

			systemEvent := map[string]interface{}{
				"cpu_usage":    cpuPercent[0],
				"memory_usage": memStats.UsedPercent,
				"total_memory": memStats.Total,
				"available_memory": memStats.Available,
			}

			ba.sendEvent("system_activity", systemEvent)
		}
	}
}

// sendEvent sends an event to the processing pipeline
func (ba *BehavioralAgent) sendEvent(eventType string, eventData interface{}) {
	event := Event{
		UserID:      ba.userID,
		EventType:   eventType,
		Timestamp:   time.Now(),
		EventData:   map[string]interface{}{"data": eventData},
		ProcessedAt: time.Now(),
	}

	// Send to Redis queue
	eventJSON, err := json.Marshal(event)
	if err != nil {
		log.Printf("Error marshaling event: %v", err)
		return
	}

	err = ba.redisClient.LPush(ba.ctx, "behavioral_events", eventJSON).Err()
	if err != nil {
		log.Printf("Error sending event to Redis: %v", err)
	}

	// Send to WebSocket if connected
	if ba.wsConn != nil {
		err = ba.wsConn.WriteJSON(event)
		if err != nil {
			log.Printf("Error sending event via WebSocket: %v", err)
		}
	}
}

// Helper methods for data generation (placeholders for actual OS integration)

func (ba *BehavioralAgent) generateKeystrokeEvent(lastTime *time.Time, sequence *[]int) *KeystrokeEvent {
	// This is a placeholder - in production, this would capture real keystroke data
	now := time.Now()
	if lastTime.IsZero() {
		*lastTime = now
		return nil
	}

	dwellTime := float64(now.Sub(*lastTime).Nanoseconds()) / 1000000.0 // milliseconds
	*lastTime = now

	return &KeystrokeEvent{
		KeyCode:     65 + (len(*sequence) % 26), // A-Z
		DwellTime:   dwellTime,
		FlightTime:  dwellTime * 0.8,
		Pressure:    0.5 + (float64(len(*sequence)%50) / 100.0),
		TypingSpeed: 60.0 + (float64(len(*sequence)%40) - 20),
		Sequence:    fmt.Sprintf("seq_%d", len(*sequence)),
	}
}

func (ba *BehavioralAgent) generateMouseEvent(lastX, lastY *int, lastTime *time.Time) *MouseEvent {
	// Placeholder mouse event generation
	now := time.Now()
	newX := *lastX + (int(now.Unix()) % 21) - 10  // -10 to +10 movement
	newY := *lastY + (int(now.Unix()) % 21) - 10

	if !lastTime.IsZero() {
		deltaTime := float64(now.Sub(*lastTime).Nanoseconds()) / 1000000000.0 // seconds
		deltaX := float64(newX - *lastX)
		deltaY := float64(newY - *lastY)
		velocity := math.Sqrt(deltaX*deltaX + deltaY*deltaY) / deltaTime

		*lastX, *lastY = newX, newY
		*lastTime = now

		return &MouseEvent{
			X:            newX,
			Y:            newY,
			Velocity:     velocity,
			Acceleration: velocity * 0.1, // Simplified
			ClickType:    "move",
			Pressure:     0.0,
			Trajectory:   fmt.Sprintf("(%d,%d)", newX, newY),
		}
	}

	*lastX, *lastY = newX, newY
	*lastTime = now
	return nil
}

func (ba *BehavioralAgent) isUserProcess(proc *process.Process) bool {
	// Simplified user process detection
	// In production, this would check process ownership
	return true
}

func (ba *BehavioralAgent) getProcessFileAccess(proc *process.Process) []FileAccessEvent {
	// Placeholder for file access monitoring
	// In production, this would use OS-specific APIs to monitor file system events
	events := []FileAccessEvent{}

	// Simulate some file access events
	name, _ := proc.Name()
	if name != "" {
		events = append(events, FileAccessEvent{
			FilePath:    fmt.Sprintf("/tmp/file_%d.txt", proc.Pid),
			AccessType:  "read",
			FileSize:    1024,
			FileType:    "text",
			ProcessName: name,
			AccessTime:  time.Now(),
			Permissions: "r--",
		})
	}

	return events
}

func (ba *BehavioralAgent) getNetworkActivity() []NetworkEvent {
	// Placeholder for network monitoring
	// In production, this would monitor actual network connections
	events := []NetworkEvent{}

	// Simulate network activity
	events = append(events, NetworkEvent{
		DestinationIP:   "8.8.8.8",
		DestinationPort: 443,
		Protocol:        "HTTPS",
		DataVolume:      1024,
		Domain:          "google.com",
		RequestType:     "GET",
		UserAgent:       "ZehraGuard-Agent/1.0",
	})

	return events
}

// Main function for standalone agent
func main() {
	userID := os.Getenv("ZEHRAGUARD_USER_ID")
	if userID == "" {
		userID = "default_user"
	}

	config := &AgentConfig{
		RedisAddr:         "localhost:6379",
		RedisPassword:     "redis_password_123",
		RedisDB:           0,
		ServerURL:         "ws://localhost:8000",
		CollectKeystrokes: true,
		CollectMouse:      true,
		CollectFiles:      true,
		CollectNetwork:    true,
		SampleRate:        10,
	}

	agent := NewBehavioralAgent(userID, config)

	// Handle graceful shutdown
	go func() {
		// Wait for interrupt signal
		time.Sleep(time.Hour) // In production, use proper signal handling
		agent.Stop()
	}()

	if err := agent.Start(); err != nil {
		log.Fatalf("Agent failed: %v", err)
	}
}
