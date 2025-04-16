import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  Container,
  Grid,
  Paper,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  CircularProgress,
  Divider,
  Card,
  CardContent,
  CardActions,
  IconButton,
} from "@mui/material";
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  ArrowForward as ArrowForwardIcon,
  ArrowBack as ArrowBackIcon,
} from "@mui/icons-material";
import axios from "axios";
import { format } from "date-fns";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { id } from "date-fns/locale";

const API_URL = "http://127.0.0.1:5000";

const statusColumns = [
  { id: "todo", title: "To Do" },
  { id: "in_progress", title: "In Progress" },
  { id: "completed", title: "Completed" },
];

function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    status: "todo",
    priority: "medium",
    due_date: "",
    project_id: "",
  });

  const getTasksByStatus = () => {
    const grouped = {};
    statusColumns.forEach((column) => {
      grouped[column.id] = tasks.filter((task) => task.status === column.id);
    });
    return grouped;
  };

  const tasksByStatus = getTasksByStatus();

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      const token = localStorage.getItem("token");
      const task = tasks.find((task) => task.id === taskId);

      if (!task) {
        return;
      }

      const updatedTask = { ...task, status: newStatus };

      await axios.put(
        `${API_URL}/api/tasks/${taskId}`,
        { status: newStatus },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setTasks(tasks.map((t) => (t.id === taskId ? updatedTask : t)));
    } catch (error) {
      console.error("Failed to update task status:", error);
    }
  };

  const onDragEnd = (result) => {
    const { destination, source, draggableId } = result;
    if (
      !destination ||
      (destination.droppableId === source.droppableId &&
        destination.index === source.index)
    ) {
      return;
    }

    if (destination.droppableId !== source.droppableId) {
      const taskId = parseInt(draggableId.replace("task-", ""));
      handleStatusChange(taskId, destination.droppableId);
    }
  };

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(`${API_URL}/api/tasks`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        setTasks(response.data);
      } catch (error) {
        setError("Failed to fetch tasks");
      } finally {
        setLoading(false);
      }
    };

    const fetchProjects = async () => {
      try {
        const token = localStorage.getItem("token"); // Assuming token is stored in localStorage
        const response = await axios.get(`${API_URL}/api/projects`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        setProjects(response.data);
      } catch (error) {
        setError("Failed to fetch projects");
      }
    };

    fetchTasks();
    fetchProjects();
  }, []);

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setFormData({
      title: "",
      description: "",
      status: "todo",
      priority: "medium",
      due_date: "",
      project_id: "",
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem("token");
      const postResponse = await axios.post(`${API_URL}/api/tasks`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const getResponse = await axios.get(`${API_URL}/api/tasks`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setTasks(getResponse.data);
      handleClose();
    } catch (error) {
      setError("Failed to create task");
    }
  };

  const handleDelete = async (taskid) => {
    try {
      const token = localStorage.getItem("token");
      await axios.delete(`${API_URL}/api/tasks/${taskid}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const getResponse = await axios.get(`${API_URL}/api/tasks`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setTasks(getResponse.data);
    } catch (error) {
      console.error("Failed to delete task:", error);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "high":
        return "error";
      case "medium":
        return "warning";
      case "low":
        return "success";
      default:
        return "default";
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "completed":
        return "success";
      case "in_progress":
        return "warning";
      case "todo":
        return "default";
      default:
        return "default";
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
      <Box
        sx={{
          mb: 4,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Typography variant="h4">Tasks</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpen}
        >
          New Task
        </Button>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {/* Kanban Board */}
      <DragDropContext onDragEnd={onDragEnd}>
        <Grid container spacing={2}>
          {statusColumns.map((column) => (
            <Grid item xs={12} md={4} key={column.id}>
              <Paper
                sx={{
                  p: 2,
                  height: "100%",
                  bgcolor:
                    column.id === "completed"
                      ? "rgba(76, 175, 80, 0.04)"
                      : column.id === "in_progress"
                        ? "rgba(255, 152, 0, 0.04)"
                        : "rgba(0, 0, 0, 0.04)",
                  border: "1px solid",
                  borderColor:
                    column.id === "completed"
                      ? "rgba(76, 175, 80, 0.1)"
                      : column.id === "in_progress"
                        ? "rgba(255, 152, 0, 0.1)"
                        : "rgba(0, 0, 0, 0.1)",
                }}
              >
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    mb: 2,
                  }}
                >
                  <Typography variant="h6">{column.title}</Typography>
                  <Chip
                    label={tasksByStatus[column.id].length}
                    color={
                      column.id === "completed"
                        ? "success"
                        : column.id === "in_progress"
                          ? "warning"
                          : "default"
                    }
                    size="small"
                  />
                </Box>
                <Divider sx={{ mb: 2 }} />

                <Droppable droppableId={column.id}>
                  {(provided) => (
                    <Box
                      {...provided.droppableProps}
                      ref={provided.innerRef}
                      sx={{ minHeight: "50vh" }}
                    >
                      {tasksByStatus[column.id].map((task, index) => (
                        <Draggable
                          key={`task-${task.id}`}
                          draggableId={`task-${task.id}`}
                          index={index}
                        >
                          {(provided) => (
                            <Card
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              sx={{ mb: 2, "&:hover": { boxShadow: 3 } }}
                            >
                              <CardContent>
                                <Typography variant="h6" gutterBottom>
                                  {task.title}
                                </Typography>
                                <Typography
                                  variant="body2"
                                  color="text.secondary"
                                  sx={{ mb: 1 }}
                                >
                                  {task.description}
                                </Typography>
                                <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
                                  <Chip
                                    label={task.priority}
                                    size="small"
                                    color={getPriorityColor(task.priority)}
                                  />
                                </Box>
                                {task.due_date && (
                                  <Typography
                                    variant="body2"
                                    color="text.secondary"
                                  >
                                    Due:{" "}
                                    {format(
                                      new Date(task.due_date),
                                      "MMM d, yyyy"
                                    )}
                                  </Typography>
                                )}
                                {task.project && (
                                  <Typography
                                    variant="body2"
                                    color="text.secondary"
                                  >
                                    Project: {task.project.name}
                                  </Typography>
                                )}
                              </CardContent>
                              <CardActions
                                sx={{ justifyContent: "space-between" }}
                              >
                                <Box>
                                  {column.id !== "todo" && (
                                    <IconButton
                                      size="small"
                                      onClick={() =>
                                        handleStatusChange(
                                          task.id,
                                          column.id === "in_progress"
                                            ? "todo"
                                            : "in_progress"
                                        )
                                      }
                                    >
                                      <ArrowBackIcon fontSize="small" />
                                    </IconButton>
                                  )}
                                  {column.id !== "completed" && (
                                    <IconButton
                                      size="small"
                                      onClick={() =>
                                        handleStatusChange(
                                          task.id,
                                          column.id === "todo"
                                            ? "in_progress"
                                            : "completed"
                                        )
                                      }
                                    >
                                      <ArrowForwardIcon fontSize="small" />
                                    </IconButton>
                                  )}
                                </Box>
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => handleDelete(task.id)}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </CardActions>
                            </Card>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </Box>
                  )}
                </Droppable>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </DragDropContext>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Create New Task</DialogTitle>
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
            <Button onClick={handleClose}>Cancel</Button>
            <Button type="submit" variant="contained">
              Create
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Container>
  );
}

export default Tasks;
