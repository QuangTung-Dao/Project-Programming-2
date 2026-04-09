SOLAR SYSTEM SIMULATION

1. Introduction  
	- The "Solar System Simulation" is an interactive, real-time visualization software that models the motion of celestial bodies within a simplified solar system. Built using a 2D graphics framework, the application combines **classical physics**, **data visualization**, and **user interaction design** to create an engaging and educational experience.  
	- The system allows users to:  
		* Observe planetary motion based on gravitational forces.  
		* Interact with the simulation through camera controls and selection tools.  
		* Monitor real-time physical parameters such as velocity, distance, and time progression.  
	- Similarly, we apply OOP and data encapsulation, data organization, and classification to connect physical phenomena (planetary orbits) and UI interaction.  
	- Our product focuses heavily on optimizing logic by coding in pure Python, not using other supporting libraries like MuJoCo for simulation. Instead, we want to build our own logic code to create the simulation.  
2. Library  
	- In this project, we use 3 libraries to run the simulation, which are pygame, random, and math library.  
	- We decided not to use advanced libraries like Mujoco, OpenCV, Tkinter, etc. Instead, we used simple libraries because our project focuses heavily on logic code, including:  
		* Transforming complex physics equations into code that computers can understand, applying advanced physics equations to optimize the accuracy of planetary parameters and orbital motion.  
		* We want to emphasize building logic to create simulated UI interfaces and interact with the mouse and keyboard without using other frameworks, HTML, or Java, but simply using Python and the logic surrounding it.  
3. Algorithm  
	- At first, we planned to use the Euler method to simulate the solar system. However, we realized that if we continued using this method, the error would increase over time. Therefore, the Euler-Cromer method will become our method to simulate the solar system.  
	- So what is the difference between these two methods? We will consider a system involving velocity and position.  
		* **Euler method**: uses the velocity from the beginning of the time interval to calculate the new position.  
		  + v_new= v_old +a_old * dt   
		  + x_new= x_old +v_old * dt   
		-> Calculations are always based on outdated data. This creates a cumulative error that causes the object to deviate from its trajectory even further. The system continuously receives additional fictitious energy, making the trajectory unstable.  
		* **Euler-Cromer method**: updates the velocity first, then uses this new velocity to calculate the new position.  
		  + v_new= v_old + a_old * dt   
		  + x_new= x_old + v_new * dt   
	- Using v_new creates an error compensation. If the error in the initial steps increases the energy, then in later steps (when using the new velocity), the error will cause the energy to decrease. As a result, the overall energy fluctuates around a fixed value instead of increasing indefinitely.  
4. About the User Interface (UI)  
	4.1. Layout structure (Overview)  
		* The interface uses a **multi-pane**, **fixed layout** to display all key information without extra navigation.  
		* The interface is divided into three main regions:  
			* **The Sidebar** (Left Panel) displays the planet list and detailed information.  
			* **The Main Canvas** (Center) is where the simulation visualization runs.  
			* **HUD** (Top-right Corner) for viewing system status and controls.  
	4.2. Sidebar (Control Panel)
	   The sidebar serves as the main control and information hub.
			4.2.1. Planet List (Interactive Table)  
				* Each planet (from Mercury to Neptune) is represented as a **row-based UI component** with the following structure:  
			  		* A small colored circle representing the planet.  
			 		  * The planet’s name.  
			 		  * Distance: real-time distance in Astronomical Units (AU).  
      4.2.2. Interactive States  
				* **Default state:**  
  					* Dark, semi-transparent background.  
  					* White text.  
  					* Let Earth be the initial state of choice.  
				* **Hover state:**  
  					* Slightly brighter background.  
  					* Subtle visual cue (arrow indicator).  
				* **Selected state:**  
  					* Highlighted background (blue tone).  
  					* Cyan text color.  
  					* Left-side accent bar (bright blue).  
       4.2.3. Dynamic Data Binding  
			  * Each row automatically updates the distance to the Sun (converted to AU in real time).  
			  * This ensures that the sidebar acts as a **live data dashboard** rather than static content.  
			 4.2.4. Detailed Information Panel  
				* When a planet is selected, a detailed panel appears below the list.
  					* **Layout Structure:**
               * Header with planet name and color indicator.  
               * Structured key-value rows.
  					* **Displayed Parameters:**
    						* Distance (AU and km).  
    						* Orbital speed (km/s).  
    						* Simulation days.  
    						* Mass (kg).  
       4.2.5. Instruction Section  
				* A command block is displayed at the bottom of the sidebar.  
  					* Click row/planet: select.  
  					* Scroll: zoom.  
  					* Right-drag: pan camera.  
  					* L: appears/disappears labels.  
  					* SPACE: pause.  
  					* +/-: simulation speed.  
  	4.3. Main Canvas (Simulation View)  
     		4.3.1. Tooltip System (Contextual UI)  
			    * The tooltip is a **floating UI component** that:  
 		    	  * Anchors near the chosen planet.  
  				  * Automatically repositions to always be visible on the screen.
			    * **Contents:**
  				  * Planet name (highlighted).  
  				  * Distance (AU and km).  
  				  * Orbital speed (km/s).  
  				  * Simulation time.  
  				  * Mass (kg).  
  	4.4. HUD (Heads-Up Display)  
     		4.4.1. Dynamic Status Indicators  
			    * Speed: exponential scaling (1x, 2x, 4x,...).  
			    * Whether the simulation is paused.  
			    * Zoom: current zoom level (default is 1.00x).  
			    * Total elapsed days.  
  		  4.4.2. Visual Feedback  
			    * Color coding:  
  				  * Cyan → currently running.  
  				  * Red → paused.  
			    * Icons:  
  				  * ▶ for running.  
  				  * ⏸ for paused.  
5. About the User Experience (UX)  
   	5.1. Camera Interaction Model
        5.1.1. Zooming  
			      * Controlled by mouse scroll.  
			      * Zooms in/out easily.  
			      * Focuses on the mouse position.  
  	    5.1.2. Panning  
			      * Done by right-clicking.  
		      	* Allows users to move freely around the screen.  
  	  	5.1.3. Reset  
			      * Instantly restores zoom to 1.00x and center position by pressing “R”.  
  	5.2. Selection Mechanism  
		  * On the sidebar: click directly on the planet name.    
		  * From the canvas: click near the planet, and the system will detect the closest object.  
		  * When the planet is selected, it will be highlighted, a tooltip appears, and information will be updated in the sidebar and the tooltip box.

