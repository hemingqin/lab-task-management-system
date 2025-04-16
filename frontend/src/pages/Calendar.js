import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
} from "@mui/material";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000";

function Calendar() {
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedDate, setSelectedDate] = useState(null);
  const [openTaskForm, setOpenTaskForm] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    status: "todo",
    priority: "medium",
    due_date: "",
    project_id: "",
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem("token");
        const [tasksResponse, projectsResponse] = await Promise.all([
          axios.get(`${API_URL}/api/tasks`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),
          axios.get(`${API_URL}/api/projects`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),
        ]);

        setTasks(tasksResponse.data);
        setProjects(projectsResponse.data);
      } catch (error) {
        setError("Failed to fetch data");
        console.error("Error fetching calendar data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Format tasks for calendar events
  const getCalendarEvents = () => {
    return tasks.map((task) => {
      // Get the project for this task
      const project = projects.find((p) => p.id === task.project_id) || {};

      // Set color based on priority
      let backgroundColor;
      switch (task.priority) {
        case "high":
          backgroundColor = "#f44336"; // red
          break;
        case "medium":
          backgroundColor = "#ff9800"; // orange
          break;
        case "low":
          backgroundColor = "#4caf50"; // green
          break;
        default:
          backgroundColor = "#2196f3"; // blue
      }

      return {
        id: task.id,
        title: task.title,
        start: task.due_date,
        allDay: true,
        backgroundColor,
        borderColor: backgroundColor,
        extendedProps: {
          description: task.description,
          status: task.status,
          priority: task.priority,
          project: project.name,
        },
      };
    });
  };

  const handleDateClick = (arg) => {
    setSelectedDate(arg.dateStr);
    setFormData({
      ...formData,
      due_date: arg.dateStr,
    });
    setOpenTaskForm(true);
  };

  const handleEventClick = (arg) => {
    const taskId = parseInt(arg.event.id);
    const task = tasks.find((t) => t.id === taskId);

    if (task) {
      alert(
        `Task: ${task.title}\nStatus: ${task.status}\nPriority: ${task.priority}\nDescription: ${task.description}`
      );
    }
  };

  const handleCloseForm = () => {
    setOpenTaskForm(false);
    setFormData({
      title: "",
      description: "",
      status: "todo",
      priority: "medium",
      due_date: selectedDate || "",
      project_id: "",
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem("token");
      await axios.post(`${API_URL}/api/tasks`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const response = await axios.get(`${API_URL}/api/tasks`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setTasks(response.data);
      handleCloseForm();
    } catch (error) {
      setError("Failed to create task");
      console.error("Error creating task:", error);
    }
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="60vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4">Task Calendar</Typography>
        <Typography variant="body1" color="text.secondary">
          View and manage tasks by due date
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 2, mb: 4 }}>
        <Box sx={{ height: "70vh" }}>
          <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
            initialView="dayGridMonth"
            headerToolbar={{
              left: "prev,next today",
              center: "title",
              right: "dayGridMonth,timeGridWeek,timeGridDay",
            }}
            events={getCalendarEvents()}
            eventClick={handleEventClick}
            dateClick={handleDateClick}
            height="100%"
          />
        </Box>
      </Paper>

      {/* Create Task Dialog */}
      <Dialog open={openTaskForm} onClose={handleCloseForm}>
        <DialogTitle>Create Task for {selectedDate}</DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Task Title"
              fullWidth
              required
              value={formData.title}
              onChange={(e) =>
                setFormData({ ...formData, title: e.target.value })
              }
            />
            <TextField
              margin="dense"
              label="Description"
              fullWidth
              multiline
              rows={4}
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
            />
            <FormControl fullWidth margin="dense">
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.status}
                label="Status"
                onChange={(e) =>
                  setFormData({ ...formData, status: e.target.value })
                }
              >
                <MenuItem value="todo">To Do</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth margin="dense">
              <InputLabel>Priority</InputLabel>
              <Select
                value={formData.priority}
                label="Priority"
                onChange={(e) =>
                  setFormData({ ...formData, priority: e.target.value })
                }
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth margin="dense">
              <InputLabel>Project</InputLabel>
              <Select
                value={formData.project_id}
                label="Project"
                onChange={(e) =>
                  setFormData({ ...formData, project_id: e.target.value })
                }
                required
              >
                {projects.map((project) => (
                  <MenuItem key={project.id} value={project.id}>
                    {project.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              margin="dense"
              label="Due Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              value={formData.due_date}
              onChange={(e) =>
                setFormData({ ...formData, due_date: e.target.value })
              }
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseForm}>Cancel</Button>
            <Button type="submit" variant="contained">
              Create
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Container>
  );
}
export default Calendar;
