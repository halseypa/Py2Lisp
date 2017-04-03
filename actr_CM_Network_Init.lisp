(defparameter *trial-counter* 1)
(defparameter *ml-tree* 'nil)
(defparameter *mlTree-data* 'nil)

;;change to directory containing "IBLTgui...-EXBAL_Server.lisp"
(load "C:/Users/1513290957/Desktop/actr6_r1227/actr6_r1227/load-act-r-6.lisp")
;(load "C:/Users/1513290957/Desktop/actr6_r1227/actr6_r1227/IBLTguidance-EZBAL_Multiple_Cost_ALLCODE.lisp")
;(load "C:/Users/1513290957/Desktop/actr6_r1227/actr6_r1227/IBLTguidance-EZBAL_Multiple_Cost_ALLCODE_noCuesChecked.lisp")
(load "C:/Users/1513290957/Desktop/actr6_r1227/actr6_r1227/IBLTguidance-EZBAL_Rev5.lisp")
(load "C:/Users/1513290957/Desktop/actr6_r1227/actr6_r1227/actr_mltreeFDBK_Final_Branch01.lisp")

;(load ".../Desktop/actr6_r1227/actr6_r1227/load-act-r-6.lisp")
;(load ".../Desktop/actr6_r1227/actr6_r1227/IBLTguidance-EZBAL.lisp")

;initializes *input-stream* to start send-receive multi loop
(defparameter *input-stream* '(1))

;;run multiple instances of "send-receive" function
;;and continues running until 'nil/empty list is received
(defun batch-multirun-seq (runs port)
  (dotimes (i runs)
	(multirun-seq port)
	;; reset env generator
	
	;; reset model:
	(reset)
	(setf *trial-counter* 1)
	))


;;change to loop until the total trial numbers
(defun multirun-seq (port)
  (loop
     do (funcall #'send-receive port)
     ;until (equal *input-stream* '()))
	until (equal *trial-counter* '268))
  (export-allData))

;; code to work with Linkable Environment Generator over the network
;; when connected, sends out a flag to get next ENV, run function to compute ACTR-CM, then returns the answer
;; paired with the Py2Lisp.py bridge file
(defun send-receive (port)
   (let ((socket (usocket:socket-connect "127.0.0.1" port
					:element-type 'character)))
    (unwind-protect 
	 (progn
	   ;calls function in Py
	   (format (usocket:socket-stream socket) "1 ~C~%" #\return)
	   (force-output (usocket:socket-stream socket))
	   ;waits + reads data from Py
	   (usocket:wait-for-input socket)
					;(print
	    (setq *input-stream*
	       (string-to-list
		(read-line (usocket:socket-stream socket) nil nil)))
	    (setq *mlTree-data*
		  (string-to-list
		   (read-line (usocket:socket-stream socket) nil nil)))
	    (setq trialNum
		  (string-to-list
			(read-line (usocket:socket-stream socket) nil nil)))
		;)
		;(setf *resp* (first resp-and-trialNum))
		(setf trialNum (first trialNum))

	   ;; ACTR CM function ;;
	    ;; *ml-tree* function goes first to make sure chunks are created
	    ;;before the main code is executed
	    (unless (eq *input-stream* 'nil)
	      (progn
		(with-open-file (my-stream "input-data.txt"
                     			:direction :output
                     			:if-exists :append
                     			:if-does-not-exist :create)
  			(print *input-stream* my-stream))
		;(main *mlTree-data*)
		;(main '(0))
		(do-trial trialNum *input-stream*))
	     'nil)
	   
	   ;debug statements for MLTree: need to uncomment appropriate code in Py2Lisp to work
	   ;(format (usocket:socket-stream socket) (write-to-string *ml-tree*))
	   ;(force-output (usocket:socket-stream socket))
	   ;returns response back to Py
	   (format (usocket:socket-stream socket) (write-to-string *response*))
	   (force-output (usocket:socket-stream socket))
	   (setf *trial-counter* (1+ *trial-counter*))
	      );end progn
	     );end unwind
    );end let
   );end send-receive



;;paired with (send-receive) function. does what it sys...
;;converts incoming string to a list for Lisp manipulation
(defun string-to-list (str)
  (cond ((eq str "0")(setf str '()))
	(t
	 (if (not (streamp str))
	     (string-to-list (make-string-input-stream str))
	     (if (listen str)
		 (cons (read str)(string-to-list str))
		 nil))
	 );end of string-to-list
	);end of cond
  );end of string-to-list function


;;exports data from ACTR into a formatted .csv file
;; currently set export with generic file name in source code directory

(defun export-allData ()
  (with-open-file (stream (format nil "actr_data_~A.csv" (get-universal-time)) :direction :output :if-exists :append :if-does-not-exist :create)
    (format stream "Run,Trial,Stim,Thresh,ACC,Hit,CR,Miss,FA,RT,Cues-Viewed,First-cue,Sec-cue,Third-cue,RespGiven,c1Val,c2Val,c3Val~%")
    (dolist (trl (reverse *allTrials*))
          (format stream "~a,~a,~a,~a,~a,~a,~a,~a,~a,~a,~a,~a,~a,~a,~a,~a,~a,~a~%" 
                  (trial-iter trl)
                  (trial-num trl)
                  (trial-stim trl)
                  (trial-thresh trl)
                  (trial-acc trl)
                  (trial-hit trl)
                  (trial-cr trl)
                  (trial-miss trl)
                  (trial-fa trl)
                  (trial-rt trl)
                  (trial-n-cues-viewed trl)
                  (trial-first-cue trl)
                  (trial-sec-cue trl)
                  (trial-third-cue trl)
                  (trial-resp-given trl) 
                  (trial-c1Val trl)
                  (trial-c2Val trl)
                  (trial-c3Val trl)
                  ))
          );;end dolist
        (setf *allTrials* nil)
	)

