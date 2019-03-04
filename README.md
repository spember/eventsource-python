## Python Event Source Test

This is an attempt to create an example of Event Sourcing within a Python / Django application. 

This is pretty lighteight / minor. Currently it just has some event persistence, basic
validation and event generation hidden behind service layers, and some examples of constraints on 
handling events / persisting them (e.g. do not allow events to be saved with gaps in between revision 
numbers).

### What's missing / TODO

* Projection example to facilitate easy querying (e.g. current state of all restaurants)
* Snapshots
* Relations
* It's basically just tests at this point, there's no real API to communicate
* No UI

### Challenges

One should never blame the tools, but some aspects of Python and Django make this a bit more onerous than some more 
type-safe languages. For example, lack of method overloading in Python makes registering event handling on an object
to require a few more steps with individual methods. The Django ORM appears to lack an ability to cleanly construct 
Views of data and then cast them into an object, as well as the ability to cast a general query
into a non-Model object.  